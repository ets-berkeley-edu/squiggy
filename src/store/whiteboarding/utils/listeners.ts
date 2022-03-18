import fabricator from '@/store/whiteboarding/utils/fabricator'

const init = (state: any) => {
  $_addModalListeners()
  $_addViewportListeners(state)
}

export default {
  init
}

const $_addModalListeners = () => {
  // TODO: Set the toolbar back to move mode when the asset and export tooltips are hidden.
  // state.$on('tooltip.hide', function(ev, $tooltip) {
  //   if ((state.mode === 'asset' && $tooltip.$id === 'whiteboards-board-asset-trigger') || (state.mode === 'export' && $tooltip.$id === 'whiteboards-board-export-trigger')) {
  //     state.mode = 'move'
  //   }
  // })
  // // Change the drawing color when a new color has been selected in the color picker
  // state.$watch('draw.selected.color', () => p.$canvas.freeDrawingBrush.color = state.draw.selected.color.color, true)
  // // Change the drawing line width when a new line width has been selected in the width picker
  // state.$watch('draw.selected.lineWidth', () => p.$canvas.freeDrawingBrush.width = parseInt(state.draw.selected.lineWidth, 10), true)
}

/**
 * Detect keydown events in the whiteboard to respond to keyboard shortcuts
 */
const $_addViewportListeners = (state: any) => {
  state.viewport.addEventListener('keydown', (event: any) => {
    // Remove the selected elements when the delete or backspace key is pressed
    if (event.keyCode === 8 || event.keyCode === 46) {
      fabricator.deleteActiveElements(state)
      event.preventDefault()
    } else if (event.keyCode === 67 && event.metaKey) {
      // Copy the selected elements
      state.clipboard = fabricator.getActiveElements()
    } else if (event.keyCode === 86 && event.metaKey) {
      // listeners.Paste the copied elements
      fabricator.paste(state)
    }
  }, false)
}
