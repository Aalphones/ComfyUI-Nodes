import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';

const TARGET_NODE_CLASS = 'ImageBatchLoader';
const PATHS_WIDGET_NAME = 'image_paths';
const RESET_ENDPOINT = '/batch_suite/reset';
const UPLOAD_ENDPOINT = '/upload/image';


function getPathsWidget(node) {
  return node.widgets?.find((widget) => widget.name === PATHS_WIDGET_NAME);
}

function replaceUploadedNames(node, uploadedNames) {
  const widget = getPathsWidget(node);
  if (!widget) {
    return;
  }

  widget.value = uploadedNames.join('\n');
  node.setDirtyCanvas(true, true);
}

async function uploadImage(file) {
  const body = new FormData();
  body.append('image', file);
  body.append('overwrite', 'true');

  const response = await api.fetchApi(UPLOAD_ENDPOINT, { method: 'POST', body });
  if (response.status !== 200) {
    throw new Error(`Upload failed for ${file.name}: ${response.status}`);
  }

  const data = await response.json();
  // get_annotated_filepath() resolves "subfolder/name" against ComfyUI's input/.
  return data.subfolder ? `${data.subfolder}/${data.name}` : data.name;
}

async function handleDroppedImages(node, files) {
  const uploadedNames = [];
  for (const file of files) {
    try {
      uploadedNames.push(await uploadImage(file));
    } catch (error) {
      console.error('[batch_suite]', error);
    }
  }

  if (uploadedNames.length > 0) {
    replaceUploadedNames(node, uploadedNames);
    // New images landed — reset the server cursor so the next queue run
    // starts at image 1 instead of resuming a previous batch position.
    api.fetchApi(RESET_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: TARGET_NODE_CLASS }),
    }).catch((error) => {
      console.warn('[batch_suite] cursor reset failed:', error);
    });
  }
}

function installDropHandlers(nodeType) {
  nodeType.prototype.onDragOver = function onDragOver(event) {
    const types = event?.dataTransfer?.types;
    return Boolean(types && Array.from(types).includes('Files'));
  };

  nodeType.prototype.onDragDrop = function onDragDrop(event) {
    const droppedFiles = Array.from(event?.dataTransfer?.files ?? []);
    const imageFiles = droppedFiles.filter((file) => file.type.startsWith('image/'));
    if (imageFiles.length === 0) {
      return false;
    }

    handleDroppedImages(this, imageFiles);
    // Returning true tells ComfyUI we handled the drop, so it does not spawn
    // one LoadImage node per file (the behaviour we are replacing).
    return true;
  };
}

function installApiMarker() {
  // ComfyUI only adds "upload":"image" for COMBO widgets with image_upload:true.
  // We inject the marker for ImageBatchLoader so API clients and ComfyUI's own
  // API view recognise it as an image-upload entry point.
  const originalGraphToPrompt = app.graphToPrompt.bind(app);
  app.graphToPrompt = async function graphToPrompt(...args) {
    const result = await originalGraphToPrompt(...args);
    if (result?.output) {
      for (const nodeData of Object.values(result.output)) {
        if (nodeData.class_type === TARGET_NODE_CLASS) {
          nodeData.inputs.upload = 'image';
        }
      }
    }
    return result;
  };
}

const BATCH_NODE_CLASSES = new Set(['ImageBatchLoader', 'PromptBatchLoader']);

function installAutoRequeue() {
  // Continue the batch automatically after each successful execution.
  // The cursor on the server side persists between queue runs — no reset, no
  // restart from the beginning if the run was interrupted mid-batch.
  //
  // Dedup per prompt_id: when multiple batch nodes are in the same workflow
  // (e.g. ImageBatchLoader + PromptBatchLoader), both fire 'executed' events.
  // Without dedup this would schedule two requeue calls per run. The first
  // batch node whose event arrives gets to decide whether to requeue; later
  // events for the same prompt execution are ignored.
  const requeued = new Set();

  api.addEventListener('executed', ({ detail }) => {
    const output = detail?.output;
    if (!output || output.batch_index === undefined) {
      return;
    }

    // Guard: only react to known batch nodes that are part of the currently
    // loaded canvas graph. This prevents a queued workflow from accidentally
    // triggering re-queuing of a different workflow on the canvas, and
    // prevents cross-node state sharing (ImageBatchLoader must not stop
    // PromptBatchLoader's batch and vice versa).
    const nodeId = detail?.node;
    if (nodeId === undefined) {
      return;
    }
    const node = app.graph.getNodeById(parseInt(nodeId, 10));
    if (!node || !BATCH_NODE_CLASSES.has(node.type)) {
      return;
    }

    const promptId = detail?.prompt_id;
    if (promptId !== undefined && requeued.has(promptId)) {
      return;
    }

    const currentIndex = output.batch_index[0];
    const totalItems = output.batch_total[0];
    if (currentIndex < totalItems) {
      if (promptId !== undefined) {
        requeued.add(promptId);
      }
      app.queuePrompt(0, 1);
    }
  });
}

app.registerExtension({
  name: 'batch_suite.image_batch_loader',
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name === TARGET_NODE_CLASS) {
      installDropHandlers(nodeType);
    }
  },
  setup() {
    installApiMarker();
    installAutoRequeue();
  },
});
