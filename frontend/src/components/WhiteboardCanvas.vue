<template>
  <div class="whiteboard-container">
    <div class="toolbar">
      <button @click="addStickyNote" class="btn">Add Sticky Note</button>
      <button @click="toggleDrawMode" class="btn" :class="{ active: isDrawMode }">
        {{ isDrawMode ? 'Stop Drawing' : 'Start Drawing' }}
      </button>
      <select v-model="selectedColor" class="color-select">
        <option value="yellow">Yellow</option>
        <option value="pink">Pink</option>
        <option value="blue">Blue</option>
        <option value="green">Green</option>
        <option value="orange">Orange</option>
        <option value="purple">Purple</option>
      </select>
      <button @click="deleteSelected" class="btn btn-danger" v-if="selectedNotes.length > 0">
        Delete Selected ({{ selectedNotes.length }})
      </button>
    </div>

    <div
      ref="canvas"
      class="canvas"
      @mousedown="handleCanvasMouseDown"
      @mousemove="handleCanvasMouseMove"
      @mouseup="handleCanvasMouseUp"
      @wheel="handleWheel"
      @contextmenu.prevent="handleRightClick"
      :style="canvasStyle"
    >
      <!-- SVG for drawings -->
      <svg class="drawing-layer" :style="svgStyle">
        <path
          v-for="drawing in drawings"
          :key="drawing.id"
          :d="drawing.path_data"
          :stroke="drawing.color"
          :stroke-width="drawing.stroke_width"
          fill="none"
        />
        <path
          v-if="currentPath.length > 0"
          :d="currentPathData"
          stroke="black"
          :stroke-width="2"
          fill="none"
        />
      </svg>

      <!-- Sticky Notes -->
      <div
        v-for="note in stickyNotes"
        :key="note.id"
        class="sticky-note"
        :class="{ selected: selectedNotes.includes(note.id) }"
        :style="getNoteStyle(note)"
        @mousedown.stop="handleNoteMouseDown($event, note)"
        @click.stop="selectNote(note.id, $event)"
      >
        <div class="note-header" :style="{ backgroundColor: getNoteColor(note.color) }">
          <button @click.stop="deleteNote(note.id)" class="delete-btn">×</button>
        </div>
        <div class="note-content">
          <textarea
            v-model="note.content"
            @blur="updateNote(note)"
            @click.stop
            placeholder="Type here..."
          ></textarea>
          <input
            v-if="note.link"
            type="url"
            v-model="note.link"
            @blur="updateNote(note)"
            @click.stop
            placeholder="Enter URL..."
            class="link-input"
          />
        </div>
        <div class="resize-handle" @mousedown.stop="handleResizeMouseDown($event, note)"></div>
      </div>

      <!-- Context Menu -->
      <div
        v-if="contextMenu.visible"
        class="context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <div @click="addStickyNoteAt(contextMenu.x, contextMenu.y)">Add Sticky Note</div>
        <div @click="addLinkNote(contextMenu.x, contextMenu.y)">Add Note with Link</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

export default {
  name: 'WhiteboardCanvas',
  setup() {
    const route = useRoute()
    const whiteboardId = computed(() => route.params.id)

    // Canvas state
    const canvas = ref(null)
    const zoom = ref(1)
    const panX = ref(0)
    const panY = ref(0)
    const isPanning = ref(false)
    const panStartX = ref(0)
    const panStartY = ref(0)

    // Sticky notes
    const stickyNotes = ref([])
    const selectedNotes = ref([])
    const selectedColor = ref('yellow')
    const draggedNote = ref(null)
    const dragOffset = ref({ x: 0, y: 0 })
    const resizingNote = ref(null)

    // Drawing
    const isDrawMode = ref(false)
    const drawings = ref([])
    const currentPath = ref([])
    const isDrawing = ref(false)

    // Context menu
    const contextMenu = ref({
      visible: false,
      x: 0,
      y: 0,
    })

    // WebSocket
    let ws = null

    const canvasStyle = computed(() => ({
      transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoom.value})`,
      transformOrigin: '0 0',
    }))

    const svgStyle = computed(() => ({
      width: '100%',
      height: '100%',
      position: 'absolute',
      top: 0,
      left: 0,
      pointerEvents: isDrawMode.value ? 'auto' : 'none',
    }))

    const currentPathData = computed(() => {
      if (currentPath.value.length === 0) return ''
      return (
        'M ' +
        currentPath.value
          .map((point) => `${point.x},${point.y}`)
          .join(' L ')
      )
    })

    function getNoteStyle(note) {
      return {
        left: note.x + 'px',
        top: note.y + 'px',
        width: note.width + 'px',
        height: note.height + 'px',
        zIndex: note.z_index,
      }
    }

    function getNoteColor(color) {
      const colors = {
        yellow: '#feff9c',
        pink: '#ff7eb9',
        blue: '#7afcff',
        green: '#b5ff7e',
        orange: '#ffa500',
        purple: '#d8b5ff',
      }
      return colors[color] || colors.yellow
    }

    async function loadWhiteboard() {
      try {
        const response = await api.getWhiteboard(whiteboardId.value)
        stickyNotes.value = response.data.sticky_notes || []
        drawings.value = response.data.drawings || []
      } catch (error) {
        console.error('Error loading whiteboard:', error)
      }
    }

    async function addStickyNote() {
      try {
        const response = await api.createStickyNote({
          whiteboard: whiteboardId.value,
          content: '',
          color: selectedColor.value,
          x: 100,
          y: 100,
          width: 200,
          height: 200,
          z_index: stickyNotes.value.length,
        })
        stickyNotes.value.push(response.data)
        broadcastUpdate({ type: 'note_added', note: response.data })
      } catch (error) {
        console.error('Error adding sticky note:', error)
      }
    }

    async function addStickyNoteAt(x, y) {
      try {
        const canvasRect = canvas.value.getBoundingClientRect()
        const actualX = (x - canvasRect.left - panX.value) / zoom.value
        const actualY = (y - canvasRect.top - panY.value) / zoom.value

        const response = await api.createStickyNote({
          whiteboard: whiteboardId.value,
          content: '',
          color: selectedColor.value,
          x: actualX,
          y: actualY,
          width: 200,
          height: 200,
          z_index: stickyNotes.value.length,
        })
        stickyNotes.value.push(response.data)
        broadcastUpdate({ type: 'note_added', note: response.data })
      } catch (error) {
        console.error('Error adding sticky note:', error)
      }
      contextMenu.value.visible = false
    }

    async function addLinkNote(x, y) {
      try {
        const canvasRect = canvas.value.getBoundingClientRect()
        const actualX = (x - canvasRect.left - panX.value) / zoom.value
        const actualY = (y - canvasRect.top - panY.value) / zoom.value

        const response = await api.createStickyNote({
          whiteboard: whiteboardId.value,
          content: '',
          link: 'https://',
          color: selectedColor.value,
          x: actualX,
          y: actualY,
          width: 200,
          height: 200,
          z_index: stickyNotes.value.length,
        })
        stickyNotes.value.push(response.data)
        broadcastUpdate({ type: 'note_added', note: response.data })
      } catch (error) {
        console.error('Error adding sticky note:', error)
      }
      contextMenu.value.visible = false
    }

    async function updateNote(note) {
      try {
        await api.updateStickyNote(note.id, note)
        broadcastUpdate({ type: 'note_updated', note })
      } catch (error) {
        console.error('Error updating sticky note:', error)
      }
    }

    async function deleteNote(noteId) {
      try {
        await api.deleteStickyNote(noteId)
        stickyNotes.value = stickyNotes.value.filter((n) => n.id !== noteId)
        selectedNotes.value = selectedNotes.value.filter((id) => id !== noteId)
        broadcastUpdate({ type: 'note_deleted', noteId })
      } catch (error) {
        console.error('Error deleting sticky note:', error)
      }
    }

    async function deleteSelected() {
      for (const noteId of selectedNotes.value) {
        await deleteNote(noteId)
      }
      selectedNotes.value = []
    }

    function selectNote(noteId, event) {
      if (event.ctrlKey || event.metaKey) {
        if (selectedNotes.value.includes(noteId)) {
          selectedNotes.value = selectedNotes.value.filter((id) => id !== noteId)
        } else {
          selectedNotes.value.push(noteId)
        }
      } else {
        selectedNotes.value = [noteId]
      }
    }

    function handleNoteMouseDown(event, note) {
      if (event.button === 1) return // Ignore middle mouse button

      draggedNote.value = note
      const rect = event.target.getBoundingClientRect()
      dragOffset.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      }

      // If note is selected and multiple notes are selected, prepare group drag
      if (selectedNotes.value.includes(note.id) && selectedNotes.value.length > 1) {
        // Group drag will be handled
      } else {
        selectNote(note.id, event)
      }
    }

    function handleResizeMouseDown(event, note) {
      resizingNote.value = note
      event.stopPropagation()
    }

    function handleCanvasMouseDown(event) {
      if (event.button === 1) {
        // Middle mouse button - pan
        isPanning.value = true
        panStartX.value = event.clientX - panX.value
        panStartY.value = event.clientY - panY.value
      } else if (isDrawMode.value && event.button === 0) {
        // Left mouse button in draw mode - draw
        isDrawing.value = true
        const canvasRect = canvas.value.getBoundingClientRect()
        const x = (event.clientX - canvasRect.left - panX.value) / zoom.value
        const y = (event.clientY - canvasRect.top - panY.value) / zoom.value
        currentPath.value = [{ x, y }]
      } else if (event.button === 0 && !draggedNote.value && !resizingNote.value) {
        // Clear selection when clicking on empty canvas
        selectedNotes.value = []
      }
    }

    function handleCanvasMouseMove(event) {
      if (isPanning.value) {
        panX.value = event.clientX - panStartX.value
        panY.value = event.clientY - panStartY.value
      } else if (draggedNote.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const newX = (event.clientX - canvasRect.left - panX.value) / zoom.value - dragOffset.value.x
        const newY = (event.clientY - canvasRect.top - panY.value) / zoom.value - dragOffset.value.y

        if (selectedNotes.value.length > 1 && selectedNotes.value.includes(draggedNote.value.id)) {
          // Group drag
          const deltaX = newX - draggedNote.value.x
          const deltaY = newY - draggedNote.value.y

          for (const noteId of selectedNotes.value) {
            const note = stickyNotes.value.find((n) => n.id === noteId)
            if (note) {
              note.x += deltaX
              note.y += deltaY
            }
          }
        } else {
          draggedNote.value.x = newX
          draggedNote.value.y = newY
        }
      } else if (resizingNote.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const x = (event.clientX - canvasRect.left - panX.value) / zoom.value
        const y = (event.clientY - canvasRect.top - panY.value) / zoom.value

        resizingNote.value.width = Math.max(100, x - resizingNote.value.x)
        resizingNote.value.height = Math.max(100, y - resizingNote.value.y)
      } else if (isDrawing.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const x = (event.clientX - canvasRect.left - panX.value) / zoom.value
        const y = (event.clientY - canvasRect.top - panY.value) / zoom.value
        currentPath.value.push({ x, y })
      }
    }

    async function handleCanvasMouseUp() {
      if (draggedNote.value) {
        await updateNote(draggedNote.value)
        if (selectedNotes.value.length > 1) {
          // Update all selected notes
          for (const noteId of selectedNotes.value) {
            const note = stickyNotes.value.find((n) => n.id === noteId)
            if (note && note.id !== draggedNote.value.id) {
              await updateNote(note)
            }
          }
        }
        draggedNote.value = null
      }

      if (resizingNote.value) {
        await updateNote(resizingNote.value)
        resizingNote.value = null
      }

      if (isDrawing.value && currentPath.value.length > 1) {
        try {
          const pathData = currentPathData.value
          const response = await api.createDrawing({
            whiteboard: whiteboardId.value,
            path_data: pathData,
            color: 'black',
            stroke_width: 2,
          })
          drawings.value.push(response.data)
          broadcastUpdate({ type: 'drawing_added', drawing: response.data })
        } catch (error) {
          console.error('Error saving drawing:', error)
        }
        currentPath.value = []
      }

      isPanning.value = false
      isDrawing.value = false
    }

    function handleWheel(event) {
      event.preventDefault()
      const delta = event.deltaY > 0 ? 0.9 : 1.1
      zoom.value = Math.max(0.1, Math.min(5, zoom.value * delta))
    }

    function handleRightClick(event) {
      contextMenu.value = {
        visible: true,
        x: event.clientX,
        y: event.clientY,
      }
    }

    function toggleDrawMode() {
      isDrawMode.value = !isDrawMode.value
    }

    function setupWebSocket() {
      const wsUrl = `ws://localhost:8000/ws/whiteboard/${whiteboardId.value}/`
      ws = new WebSocket(wsUrl)

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket closed, reconnecting...')
        setTimeout(setupWebSocket, 3000)
      }
    }

    function handleWebSocketMessage(data) {
      if (data.type === 'note_added') {
        const exists = stickyNotes.value.find((n) => n.id === data.note.id)
        if (!exists) {
          stickyNotes.value.push(data.note)
        }
      } else if (data.type === 'note_updated') {
        const index = stickyNotes.value.findIndex((n) => n.id === data.note.id)
        if (index !== -1) {
          stickyNotes.value[index] = data.note
        }
      } else if (data.type === 'note_deleted') {
        stickyNotes.value = stickyNotes.value.filter((n) => n.id !== data.noteId)
      } else if (data.type === 'drawing_added') {
        const exists = drawings.value.find((d) => d.id === data.drawing.id)
        if (!exists) {
          drawings.value.push(data.drawing)
        }
      }
    }

    function broadcastUpdate(data) {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data))
      }
    }

    onMounted(() => {
      loadWhiteboard()
      setupWebSocket()
      document.addEventListener('click', () => {
        contextMenu.value.visible = false
      })
    })

    onUnmounted(() => {
      if (ws) {
        ws.close()
      }
    })

    return {
      canvas,
      canvasStyle,
      svgStyle,
      stickyNotes,
      selectedNotes,
      selectedColor,
      isDrawMode,
      drawings,
      currentPath,
      currentPathData,
      contextMenu,
      getNoteStyle,
      getNoteColor,
      addStickyNote,
      addStickyNoteAt,
      addLinkNote,
      updateNote,
      deleteNote,
      deleteSelected,
      selectNote,
      handleNoteMouseDown,
      handleResizeMouseDown,
      handleCanvasMouseDown,
      handleCanvasMouseMove,
      handleCanvasMouseUp,
      handleWheel,
      handleRightClick,
      toggleDrawMode,
    }
  },
}
</script>

<style scoped>
.whiteboard-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f0f0f0;
}

.toolbar {
  background: #333;
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn {
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn:hover {
  background: #45a049;
}

.btn.active {
  background: #ff9800;
}

.btn-danger {
  background: #f44336;
}

.btn-danger:hover {
  background: #da190b;
}

.color-select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.canvas {
  flex: 1;
  position: relative;
  cursor: grab;
  background: white;
  overflow: hidden;
}

.canvas:active {
  cursor: grabbing;
}

.drawing-layer {
  pointer-events: none;
}

.sticky-note {
  position: absolute;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  cursor: move;
  user-select: none;
}

.sticky-note.selected {
  box-shadow: 0 0 0 3px #2196f3;
}

.note-header {
  padding: 5px 8px;
  border-radius: 4px 4px 0 0;
  display: flex;
  justify-content: flex-end;
}

.delete-btn {
  background: rgba(0, 0, 0, 0.2);
  border: none;
  color: white;
  font-size: 20px;
  line-height: 1;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
}

.delete-btn:hover {
  background: rgba(0, 0, 0, 0.4);
}

.note-content {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.note-content textarea {
  flex: 1;
  border: none;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  outline: none;
  background: transparent;
}

.link-input {
  width: 100%;
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 12px;
}

.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, transparent 50%, #999 50%);
  cursor: nwse-resize;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10000;
}

.context-menu div {
  padding: 8px 16px;
  cursor: pointer;
}

.context-menu div:hover {
  background: #f0f0f0;
}
</style>
