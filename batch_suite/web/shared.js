import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';

const TARGET_NODE_CLASS = 'ImageBatchLoader';
const PATHS_WIDGET_NAME = 'image_paths';
const RESET_ENDPOINT = '/batch_suite/reset';
const UPLOAD_ENDPOINT = '/upload/image';

// True while we are driving the queue ourselves, so the queue wrapper below
// does not reset the server cursor between images of the same batch run.
let isAutoQueueing = false;

function getPathsWidget(node) {
  return node.widgets?.find((widget) => widget.name === PATHS_WIDGET_NAME);
}

function appendUploadedNames(node, uploadedNames) {
  const widget = getPathsWidget(node);
  if (!widget) {
    return;
  }

  const existingLines = widget.value ? widget.value.split('\n').filter(Boolean) : [];
  widget.value = [...existingLines, ...uploadedNames].join('\n');
  node.setDirtyCanvas(true, true);
}

async function uploadImage(file) {
  const body = new FormData();
  body.append('image', file);
  body.append('overwrite', 'false');

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
    appendUploadedNames(node, uploadedNames);
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

function installAutoRequeue() {
  // Reset the server-side cursor when the user starts a fresh run, so the batch
  // begins at the first image instead of resuming a previous/aborted position.
  const originalQueuePrompt = app.queuePrompt.bind(app);
  app.queuePrompt = async function queuePrompt(number, batchCount) {
    const hasBatchLoader = app.graph.findNodesByType(TARGET_NODE_CLASS).length > 0;
    if (!isAutoQueueing && hasBatchLoader) {
      await api.fetchApi(RESET_ENDPOINT, { method: 'POST' });
    }
    return originalQueuePrompt(number, batchCount);
  };

  api.addEventListener('executed', ({ detail }) => {
    const output = detail?.output;
    if (!output || output.batch_index === undefined) {
      return;
    }

    const currentIndex = output.batch_index[0];
    const totalItems = output.batch_total[0];
    if (currentIndex < totalItems) {
      isAutoQueueing = true;
      app.queuePrompt(0, 1);
    } else {
      isAutoQueueing = false;
    }
  });

  const stopAutoQueueing = () => {
    isAutoQueueing = false;
  };
  api.addEventListener('execution_error', stopAutoQueueing);
  api.addEventListener('execution_interrupted', stopAutoQueueing);
}

app.registerExtension({
  name: 'batch_suite.image_batch_loader',
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name === TARGET_NODE_CLASS) {
      installDropHandlers(nodeType);
    }
  },
  setup() {
    installAutoRequeue();
  },
});
