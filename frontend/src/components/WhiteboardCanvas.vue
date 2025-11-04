<template>
  <div class="whiteboard-container"
       @mousedown="handleCanvasMouseDown"
       @mousemove="handleCanvasMouseMove"
       @mouseup="handleCanvasMouseUp"
       @wheel="handleWheel"
       @contextmenu.prevent="handleRightClick"
       @click="closeContextMenu">
    <div class="toolbar" @mousedown.stop @mousemove.stop @mouseup.stop @click.stop @contextmenu.stop @wheel.stop>
      <HamburgerMenu />
      <button @click="addStickyNote" class="btn">Add Sticky Note</button>
      <button @click="toggleDrawMode" class="btn" :class="{ active: isDrawMode }">
        {{ isDrawMode ? 'Stop Drawing' : 'Draw (Freehand)' }}
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
      <button @click="deleteSelectedDrawing" class="btn btn-danger" v-if="selectedDrawing">
        Delete Drawing
      </button>
      <span v-if="!isDrawMode && drawings.length > 0" class="hint-text">
        💡 Click on drawings to select them
      </span>
    </div>

    <!-- SVG for drawings (outside canvas-area so it covers the full viewport) -->
    <svg class="drawing-layer" 
         :style="svgStyle"
         @mousedown="handleSvgMouseDown"
         @mousemove="handleSvgMouseMove"
         @mouseup="handleSvgMouseUp">
      <g :transform="`translate(${panX} ${panY}) scale(${zoom})`">
        <path
          v-for="drawing in drawings"
          :key="drawing.id"
          :d="drawing.path_data"
          :stroke="drawing.color"
          :stroke-width="drawing.stroke_width"
          :class="{ 'selected-drawing': selectedDrawing === drawing.id }"
          fill="none"
          @click="selectDrawing(drawing.id)"
          style="cursor: pointer;"
        />
        <path
          v-if="currentPath.length > 0"
          :d="currentPathData"
          :stroke="selectedColor"
          :stroke-width="2"
          fill="none"
        />
      </g>
    </svg>

    <div class="canvas-area"
         ref="canvas"
         :style="canvasStyle">

      <!-- Sticky Notes -->
      <div
        v-for="note in stickyNotes"
        :key="note.id"
        class="sticky-note"
        :class="{ selected: selectedNotes.includes(note.id), editing: editingNote === note.id }"
        :style="getNoteStyle(note)"
        @mousedown.stop="handleNoteMouseDown($event, note)"
        @click.stop="selectNote(note.id, $event)"
        @dblclick.stop="startEditingNote(note.id)"
      >
        <div class="note-header">
          <button 
            @click.stop="toggleColorPicker(note.id)" 
            class="color-btn"
            title="Change color"
          >
            🎨
          </button>
          <label 
            @click.stop
            class="image-btn"
            title="Add image"
          >
            🖼️
            <input 
              type="file" 
              accept="image/*"
              @change="handleImageUpload($event, note)"
              style="display: none;"
            />
          </label>
          <button @click.stop="confirmDeleteNote(note.id)" class="delete-btn">×</button>
        </div>
        
        <!-- Color Picker Menu -->
        <div 
          v-if="showColorPicker === note.id" 
          class="color-picker"
          @click.stop
        >
          <div class="color-options">
            <button
              v-for="color in availableColors"
              :key="color"
              class="color-option"
              :style="{ backgroundColor: getNoteColor(color) }"
              @click="changeNoteColor(note.id, color)"
              :class="{ active: note.color === color }"
            ></button>
          </div>
        </div>
        <div class="note-content" @dblclick.stop="startEditingNote(note.id)">
          <!-- Image carousel -->
          <div v-if="note.images && note.images.length > 0" class="image-carousel" @click.stop>
            <button 
              v-if="note.images.length > 1" 
              @click="prevImage(note.id)" 
              class="carousel-btn prev-btn"
              title="Previous image"
            >
              ‹
            </button>
            <div class="image-container">
              <img 
                :src="getCurrentImage(note).image" 
                class="note-image"
                @click.stop
              />
              <button 
                @click="deleteCurrentImage(note)" 
                class="delete-image-btn"
                title="Delete this image"
              >
                ×
              </button>
            </div>
            <button 
              v-if="note.images.length > 1" 
              @click="nextImage(note.id)" 
              class="carousel-btn next-btn"
              title="Next image"
            >
              ›
            </button>
            <div v-if="note.images.length > 1" class="image-counter">
              {{ (currentImageIndex[note.id] || 0) + 1 }} / {{ note.images.length }}
            </div>
          </div>
          <textarea
            v-model="note.content"
            :readonly="editingNote !== note.id"
            @blur="stopEditingNote(note)"
            @click.stop
            @mousedown.stop
            placeholder="Double-click to edit..."
            ref="noteTextarea"
            :class="{ editable: editingNote === note.id }"
          ></textarea>
          <input
            v-if="note.link"
            type="url"
            v-model="note.link"
            :readonly="editingNote !== note.id"
            @blur="stopEditingNote(note)"
            @click.stop
            @mousedown.stop
            placeholder="Enter URL..."
            class="link-input"
          />
        </div>
        <div class="resize-handle" @mousedown.stop="handleResizeMouseDown($event, note)"></div>
      </div>

      <!-- Text Elements -->
      <div
        v-for="textElement in textElements"
        :key="textElement.id"
        class="text-element"
        :class="{ selected: selectedTexts.includes(textElement.id), editing: editingText === textElement.id }"
        :style="getTextStyle(textElement)"
        @mousedown.stop="handleTextMouseDown($event, textElement)"
        @click.stop="selectText(textElement.id, $event)"
        @dblclick.stop="startEditingText(textElement.id)"
      >
        <textarea
          v-model="textElement.content"
          :readonly="editingText !== textElement.id"
          @blur="stopEditingText(textElement)"
          @click.stop
          @mousedown.stop
          placeholder="Double-click to edit..."
          class="text-input"
          :class="{ editable: editingText === textElement.id }"
          :style="{ fontSize: textElement.fontSize + 'px', color: textElement.color }"
        ></textarea>
        <button @click.stop="confirmDeleteText(textElement.id)" class="text-delete-btn">×</button>
        <div class="text-resize-handle" @mousedown.stop="handleTextResizeMouseDown($event, textElement)"></div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog (outside canvas-area so it's not affected by transform) -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <h3>Delete Note</h3>
        <p>Are you sure you want to delete this sticky note?</p>
        <div class="modal-actions">
          <button @click="confirmDelete" class="btn btn-danger">Delete</button>
          <button @click="cancelDelete" class="btn">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Context Menu (outside canvas-area so it's not affected by transform) -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ 
        left: contextMenu.screenX + 'px', 
        top: contextMenu.screenY + 'px',
        transform: `scale(${contextMenu.scale})`,
        transformOrigin: 'top left'
      }"
    >
      <div @click="addStickyNoteAt(contextMenu.canvasX, contextMenu.canvasY)">Add Sticky Note</div>
      <div @click="addLinkNote(contextMenu.canvasX, contextMenu.canvasY)">Add Note with Link</div>
      <div @click="addTextAt(contextMenu.canvasX, contextMenu.canvasY)">Add Text</div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import HamburgerMenu from './HamburgerMenu.vue'

export default {
  name: 'WhiteboardCanvas',
  components: {
    HamburgerMenu,
  },
  setup() {
    const route = useRoute()
    const whiteboardId = computed(() => route.params.id)

    // Large whiteboard dimensions - much bigger than viewport for infinite feel
    const WHITEBOARD_WIDTH = ref(20000)  // Very large working area
    const WHITEBOARD_HEIGHT = ref(15000)    // Canvas state
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
    const editingNote = ref(null)
    
    // Color picker
    const showColorPicker = ref(null)
    const availableColors = ['yellow', 'pink', 'blue', 'green', 'orange', 'purple']
    
    // Image carousel
    const currentImageIndex = ref({})
    
    // Delete confirmation
    const showDeleteConfirm = ref(null)

    // Drawing
    const isDrawMode = ref(false)
    const drawings = ref([])
    const currentPath = ref([])
    const isDrawing = ref(false)
    const selectedDrawing = ref(null)

    // Text elements
    const textElements = ref([])
    const selectedTexts = ref([])
    const draggedText = ref(null)
    const editingText = ref(null)
    const resizingText = ref(null)
    const textInitialSize = ref({ width: 0, height: 0, fontSize: 0 })

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
      cursor: isPanning.value ? 'grabbing' : 'default',
    }))

    const svgStyle = computed(() => ({
      width: '100vw',
      height: 'calc(100vh - 60px)',
      position: 'fixed',
      top: '60px',
      left: 0,
      pointerEvents: isDrawMode.value ? 'auto' : 'none',
      zIndex: 1001,
    }))

    // Calculate minimum zoom to fit the large whiteboard in viewport
    const minZoom = computed(() => {
      if (!canvas.value) return 0.05
      const canvasRect = canvas.value.getBoundingClientRect()
      const scaleX = canvasRect.width / WHITEBOARD_WIDTH.value
      const scaleY = canvasRect.height / WHITEBOARD_HEIGHT.value
      // Use the smaller scale to ensure the entire whiteboard fits
      return Math.min(scaleX, scaleY)
    })

    const currentPathData = computed(() => {
      if (currentPath.value.length === 0) return ''
      return (
        'M ' +
        currentPath.value
          .map((point) => `${point.x},${point.y}`)
          .join(' L ')
      )
    })

    // Generate consistent random values for a note based on its ID
    function getRandomForNote(noteId, type) {
      // Simple hash function to generate consistent random values
      let hash = 0
      const seed = noteId.toString() + type
      for (let i = 0; i < seed.length; i++) {
        const char = seed.charCodeAt(i)
        hash = ((hash << 5) - hash) + char
        hash = hash & hash // Convert to 32-bit integer
      }
      return Math.abs(hash % 1000) / 1000 // Return value between 0 and 1
    }

    function getNoteStyle(note) {
      // Generate random rotation between -3 and 3 degrees
      const rotation = (getRandomForNote(note.id, 'rotation') - 0.5) * 6
      
      return {
        left: note.x + 'px',
        top: note.y + 'px',
        width: note.width + 'px',
        height: note.height + 'px',
        zIndex: note.z_index,
        transform: `rotate(${rotation}deg)`,
        transformOrigin: 'center center',
        backgroundColor: getNoteColor(note.color),
        '--rotation': `${rotation}deg`,
      }
    }

    function getNoteColor(color) {
      const colors = {
        yellow: '#feff7c',
        pink: '#ffb3e6',
        blue: '#7dd3fc',
        green: '#bbf7d0',
        orange: '#fed7aa',
        purple: '#ddd6fe',
      }
      return colors[color] || colors.yellow
    }

    // Allow free positioning anywhere on the infinite whiteboard
    function constrainToWhiteboard(x, y, width = 200, height = 200) {
      // No constraints - infinite whiteboard space
      return {
        x: x,
        y: y
      }
    }

    async function loadWhiteboard() {
      try {
        const response = await api.getWhiteboard(whiteboardId.value)
        stickyNotes.value = response.data.sticky_notes || []
        
        // Ensure all image URLs are absolute
        stickyNotes.value.forEach(note => {
          if (note.images) {
            note.images.forEach(img => {
              if (img.image && !img.image.startsWith('http')) {
                img.image = `http://localhost:8000${img.image}`
              }
            })
          }
        })
        
        drawings.value = response.data.drawings || []
      } catch (error) {
        console.error('Error loading whiteboard:', error)
      }
    }

    async function addStickyNote() {
      try {
        // Place note around the center (0,0) with some random offset
        const offsetX = (Math.random() - 0.5) * 400 // Random position within 400px of center
        const offsetY = (Math.random() - 0.5) * 400
        
        const constrainedPos = constrainToWhiteboard(offsetX, offsetY, 200, 200)
        const response = await api.createStickyNote({
          whiteboard: whiteboardId.value,
          content: '',
          color: selectedColor.value,
          x: constrainedPos.x,
          y: constrainedPos.y,
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
        console.log('Creating sticky note at:', {
          canvasX: x,
          canvasY: y,
          contextMenuScreenX: contextMenu.value.screenX,
          contextMenuScreenY: contextMenu.value.screenY,
          // Calculate where this will appear on screen
          expectedScreenX: (panX.value + x) * zoom.value,
          expectedScreenY: (panY.value + y) * zoom.value + 60,
          panX: panX.value,
          panY: panY.value,
          zoom: zoom.value
        })
        
        // x and y are already canvas coordinates from the context menu
        const response = await api.createStickyNote({
          whiteboard: whiteboardId.value,
          content: '',
          color: selectedColor.value,
          x: x,
          y: y,
          width: 200,
          height: 200,
          z_index: stickyNotes.value.length,
        })
        
        console.log('Sticky note created with data:', {
          id: response.data.id,
          x: response.data.x,
          y: response.data.y,
          // Where it should appear
          shouldAppearAtScreenX: (panX.value + response.data.x) * zoom.value,
          shouldAppearAtScreenY: (panY.value + response.data.y) * zoom.value + 60
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
        // x and y are already canvas coordinates from the context menu
        const response = await api.createStickyNote({
          whiteboard: whiteboardId.value,
          content: '',
          link: 'https://',
          color: selectedColor.value,
          x: x,
          y: y,
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

    function startEditingNote(noteId) {
      editingNote.value = noteId
      // Focus the textarea after Vue updates the DOM
      nextTick(() => {
        const textareas = document.querySelectorAll('.sticky-note.editing textarea')
        if (textareas.length > 0) {
          textareas[0].focus()
        }
      })
    }

    function stopEditingNote(note) {
      editingNote.value = null
      updateNote(note)
    }

    function startEditingText(textId) {
      editingText.value = textId
      nextTick(() => {
        const textareas = document.querySelectorAll('.text-element.editing textarea')
        if (textareas.length > 0) {
          textareas[0].focus()
        }
      })
    }

    function stopEditingText(textElement) {
      editingText.value = null
      updateText(textElement)
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

    function confirmDeleteNote(noteId) {
      showDeleteConfirm.value = noteId
    }

    function cancelDelete() {
      showDeleteConfirm.value = null
    }

    async function confirmDelete() {
      if (showDeleteConfirm.value) {
        await deleteNote(showDeleteConfirm.value)
        showDeleteConfirm.value = null
      }
    }

    function toggleColorPicker(noteId) {
      showColorPicker.value = showColorPicker.value === noteId ? null : noteId
    }

    async function changeNoteColor(noteId, color) {
      const note = stickyNotes.value.find(n => n.id === noteId)
      if (note) {
        note.color = color
        await updateNote(note)
        showColorPicker.value = null
      }
    }

    async function handleImageUpload(event, note) {
      const file = event.target.files[0]
      if (file) {
        try {
          const response = await api.addImageToNote(note.id, file)
          
          // Add the new image to the note's images array
          if (!note.images) {
            note.images = []
          }
          
          // Ensure the image URL is absolute
          const imageData = response.data
          if (imageData.image && !imageData.image.startsWith('http')) {
            imageData.image = `http://localhost:8000${imageData.image}`
          }
          
          note.images.push(imageData)
          
          // Set the current image index to the newly added image
          currentImageIndex.value[note.id] = note.images.length - 1
          
          broadcastUpdate({ type: 'note_updated', note })
        } catch (error) {
          console.error('Error uploading image:', error)
          console.error('Error response:', error.response?.data)
        }
      }
      // Reset the input
      event.target.value = ''
    }

    function getCurrentImage(note) {
      if (!note.images || note.images.length === 0) return null
      const index = currentImageIndex.value[note.id] || 0
      return note.images[index] || note.images[0]
    }

    function nextImage(noteId) {
      const note = stickyNotes.value.find(n => n.id === noteId)
      if (!note || !note.images || note.images.length === 0) return
      
      const currentIndex = currentImageIndex.value[noteId] || 0
      currentImageIndex.value[noteId] = (currentIndex + 1) % note.images.length
    }

    function prevImage(noteId) {
      const note = stickyNotes.value.find(n => n.id === noteId)
      if (!note || !note.images || note.images.length === 0) return
      
      const currentIndex = currentImageIndex.value[noteId] || 0
      currentImageIndex.value[noteId] = currentIndex === 0 ? note.images.length - 1 : currentIndex - 1
    }

    async function deleteCurrentImage(note) {
      if (!note.images || note.images.length === 0) return
      
      const currentIndex = currentImageIndex.value[note.id] || 0
      const imageToDelete = note.images[currentIndex]
      
      if (confirm('Delete this image?')) {
        try {
          await api.deleteNoteImage(imageToDelete.id)
          
          // Remove the image from the array
          note.images.splice(currentIndex, 1)
          
          // Adjust the current index
          if (note.images.length === 0) {
            delete currentImageIndex.value[note.id]
          } else if (currentIndex >= note.images.length) {
            currentImageIndex.value[note.id] = note.images.length - 1
          }
          
          broadcastUpdate({ type: 'note_updated', note })
        } catch (error) {
          console.error('Error deleting image:', error)
        }
      }
    }

    // Text element functions
    async function addTextAt(x, y) {
      try {
        // x and y are already canvas coordinates from the context menu
        const textElement = {
          id: Date.now(), // Temporary ID
          content: 'New Text',
          x: x,
          y: y,
          width: 200,
          height: 100,
          fontSize: 16,
          color: '#333',
          fontFamily: 'Arial, sans-serif'
        }
        
        textElements.value.push(textElement)
        saveTextElementsToLocalStorage()
        contextMenu.value.visible = false
      } catch (error) {
        console.error('Error adding text:', error)
      }
    }

    function getTextStyle(textElement) {
      const isDragging = draggedText.value && draggedText.value.id === textElement.id
      
      return {
        left: textElement.x + 'px',
        top: textElement.y + 'px',
        width: textElement.width + 'px',
        height: textElement.height + 'px',
        zIndex: 1000,
      }
    }

    function selectText(textId, event) {
      if (event.ctrlKey || event.metaKey) {
        if (selectedTexts.value.includes(textId)) {
          selectedTexts.value = selectedTexts.value.filter(id => id !== textId)
        } else {
          selectedTexts.value.push(textId)
        }
      } else {
        selectedTexts.value = [textId]
      }
    }

    function handleTextMouseDown(event, textElement) {
      if (event.button === 2) return // Ignore right-click
      
      draggedText.value = textElement
      const canvasRect = canvas.value.getBoundingClientRect()
      const mouseX = (event.clientX - canvasRect.left) / zoom.value
      const mouseY = (event.clientY - canvasRect.top) / zoom.value
      
      dragOffset.value = {
        x: textElement.x - mouseX,
        y: textElement.y - mouseY,
      }

      // Add global mouse event listeners for text dragging
      document.addEventListener('mousemove', handleGlobalMouseMove)
      document.addEventListener('mouseup', handleGlobalMouseUp)
      
      event.preventDefault()
    }

    function handleTextResizeMouseDown(event, textElement) {
      event.stopPropagation()
      resizingText.value = textElement
      textInitialSize.value = {
        width: textElement.width,
        height: textElement.height,
        fontSize: textElement.fontSize
      }
      
      // Add global mouse event listeners for text resizing
      document.addEventListener('mousemove', handleGlobalMouseMove)
      document.addEventListener('mouseup', handleGlobalMouseUp)
      
      event.preventDefault()
    }

    async function updateText(textElement) {
      // Save to localStorage since we don't have backend support yet
      saveTextElementsToLocalStorage()
      console.log('Text updated:', textElement)
    }

    function saveTextElementsToLocalStorage() {
      const storageKey = `whiteboard_${whiteboardId.value}_texts`
      localStorage.setItem(storageKey, JSON.stringify(textElements.value))
    }

    function loadTextElementsFromLocalStorage() {
      const storageKey = `whiteboard_${whiteboardId.value}_texts`
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        try {
          const loaded = JSON.parse(stored)
          // Ensure all text elements have width and height
          textElements.value = loaded.map(text => ({
            ...text,
            width: text.width || 200,
            height: text.height || 100,
            fontSize: text.fontSize || 16
          }))
        } catch (error) {
          console.error('Error loading text elements from localStorage:', error)
        }
      }
    }

    function confirmDeleteText(textId) {
      if (confirm('Are you sure you want to delete this text?')) {
        deleteText(textId)
      }
    }

    function deleteText(textId) {
      textElements.value = textElements.value.filter(t => t.id !== textId)
      selectedTexts.value = selectedTexts.value.filter(id => id !== textId)
      saveTextElementsToLocalStorage()
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
      
      // Get the actual bounding box of the transformed canvas
      const canvasRect = canvas.value.getBoundingClientRect()
      
      // Calculate the offset relative to the note's position in canvas coordinates
      const mouseX = (event.clientX - canvasRect.left) / zoom.value
      const mouseY = (event.clientY - canvasRect.top) / zoom.value
      
      dragOffset.value = {
        x: mouseX - note.x,
        y: mouseY - note.y,
      }

      // If note is selected and multiple notes are selected, prepare group drag
      if (selectedNotes.value.includes(note.id) && selectedNotes.value.length > 1) {
        // Group drag will be handled
      } else {
        selectNote(note.id, event)
      }

      // Add global mouse event listeners to handle dragging outside the element
      document.addEventListener('mousemove', handleGlobalMouseMove)
      document.addEventListener('mouseup', handleGlobalMouseUp)
      
      event.preventDefault()
    }

    function handleGlobalMouseMove(event) {
      if (draggedNote.value) {
        // Use the existing canvas mouse move logic
        handleCanvasMouseMove(event)
      }
    }

    function handleGlobalMouseUp(event) {
      if (draggedNote.value || draggedText.value) {
        // Use the existing canvas mouse up logic
        handleCanvasMouseUp()
      }
      
      // Remove global listeners
      document.removeEventListener('mousemove', handleGlobalMouseMove)
      document.removeEventListener('mouseup', handleGlobalMouseUp)
    }

    function handleResizeMouseDown(event, note) {
      resizingNote.value = note
      event.stopPropagation()
    }

    function handleCanvasMouseDown(event) {
      // Check if clicking on a drawing path (not just the SVG background)
      const isClickingPath = event.target.tagName === 'path'
      
      if (event.button === 1) {
        // Middle mouse button - pan
        isPanning.value = true
        panStartX.value = event.clientX - panX.value
        panStartY.value = (event.clientY - 60) - panY.value  // Subtract toolbar height
      } else if (event.button === 0 && !isClickingPath && !draggedNote.value && !resizingNote.value && !draggedText.value) {
        // Clear selection when clicking on empty canvas (not on a path)
        // Don't clear if in draw mode - let the drawing happen
        if (!isDrawMode.value) {
          selectedNotes.value = []
          selectedTexts.value = []
          selectedDrawing.value = null
          editingNote.value = null
          editingText.value = null
        }
      }
    }

    function handleCanvasMouseMove(event) {
      if (isPanning.value) {
        panX.value = event.clientX - panStartX.value
        panY.value = (event.clientY - 60) - panStartY.value  // Subtract toolbar height
      } else if (draggedNote.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const newX = (event.clientX - canvasRect.left) / zoom.value - dragOffset.value.x
        const newY = (event.clientY - canvasRect.top) / zoom.value - dragOffset.value.y

        if (selectedNotes.value.length > 1 && selectedNotes.value.includes(draggedNote.value.id)) {
          // Group drag without constraints
          const deltaX = newX - draggedNote.value.x
          const deltaY = newY - draggedNote.value.y

          for (const noteId of selectedNotes.value) {
            const note = stickyNotes.value.find((n) => n.id === noteId)
            if (note) {
              note.x = note.x + deltaX
              note.y = note.y + deltaY
            }
          }
        } else {
          // Single note drag without constraints
          draggedNote.value.x = newX
          draggedNote.value.y = newY
        }
      } else if (draggedText.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const newX = (event.clientX - canvasRect.left) / zoom.value + dragOffset.value.x
        const newY = (event.clientY - canvasRect.top) / zoom.value + dragOffset.value.y
        
        const constrainedPos = constrainToWhiteboard(newX, newY, 100, 30)
        draggedText.value.x = constrainedPos.x
        draggedText.value.y = constrainedPos.y
      } else if (resizingText.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const x = (event.clientX - canvasRect.left) / zoom.value
        const y = (event.clientY - canvasRect.top) / zoom.value

        const newWidth = Math.max(100, x - resizingText.value.x)
        const newHeight = Math.max(50, y - resizingText.value.y)
        
        // Scale font size proportionally based on width change
        const widthRatio = newWidth / textInitialSize.value.width
        const newFontSize = Math.max(8, Math.min(200, textInitialSize.value.fontSize * widthRatio))
        
        resizingText.value.width = newWidth
        resizingText.value.height = newHeight
        resizingText.value.fontSize = Math.round(newFontSize)
      } else if (resizingNote.value) {
        const canvasRect = canvas.value.getBoundingClientRect()
        const x = (event.clientX - canvasRect.left) / zoom.value
        const y = (event.clientY - canvasRect.top) / zoom.value

        resizingNote.value.width = Math.max(100, x - resizingNote.value.x)
        resizingNote.value.height = Math.max(100, y - resizingNote.value.y)
      }
      // Drawing is now handled by SVG event handlers
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

      if (draggedText.value) {
        await updateText(draggedText.value)
        draggedText.value = null
      }

      if (resizingText.value) {
        await updateText(resizingText.value)
        resizingText.value = null
      }

      if (resizingNote.value) {
        await updateNote(resizingNote.value)
        resizingNote.value = null
      }

      // Drawing save is now handled by SVG mouseup handler
      isPanning.value = false
    }

    function handleWheel(event) {
      event.preventDefault()
      
      const delta = event.deltaY > 0 ? 0.9 : 1.1
      
      // Dynamic zoom limits: min to fit whiteboard exactly, max 8x
      const maxZoom = 8.0
      
      // Get canvas bounding rect
      const canvasRect = canvas.value.getBoundingClientRect()
      
      // Get mouse position relative to canvas
      const mouseX = event.clientX - canvasRect.left
      const mouseY = event.clientY - canvasRect.top
      
      // Calculate canvas coordinates at mouse position (before zoom)
      const canvasX = mouseX / zoom.value
      const canvasY = mouseY / zoom.value
      
      // Apply zoom
      const newZoom = zoom.value * delta
      zoom.value = Math.max(minZoom.value, Math.min(maxZoom, newZoom))
      
      // Calculate new mouse position in canvas after zoom
      const newMouseX = canvasX * zoom.value
      const newMouseY = canvasY * zoom.value
      
      // Adjust pan to keep the canvas point under the mouse
      // The difference between old and new mouse positions tells us how much to adjust pan
      const deltaX = mouseX - newMouseX
      const deltaY = mouseY - newMouseY
      
      panX.value += deltaX
      panY.value += deltaY
    }

    function handleRightClick(event) {
      // Get the actual bounding box of the transformed canvas
      const canvasRect = canvas.value.getBoundingClientRect()
      
      // Calculate canvas coordinates from the bounding rect
      const canvasX = (event.clientX - canvasRect.left) / zoom.value
      const canvasY = (event.clientY - canvasRect.top) / zoom.value
      
      console.log('Right click:', {
        clientX: event.clientX,
        clientY: event.clientY,
        canvasRectLeft: canvasRect.left,
        canvasRectTop: canvasRect.top,
        panX: panX.value,
        panY: panY.value,
        zoom: zoom.value,
        canvasX,
        canvasY,
        // Verify: if we place a note at canvasX, canvasY, where will it appear?
        verifyScreenX: canvasRect.left + canvasX * zoom.value,
        verifyScreenY: canvasRect.top + canvasY * zoom.value
      })
      
      // Calculate scale for the context menu
      const menuScale = Math.max(0.7, Math.min(1.5, zoom.value))
      
      contextMenu.value = {
        visible: true,
        screenX: event.clientX, // Screen coordinates for menu positioning
        screenY: event.clientY,
        canvasX: canvasX,       // Canvas coordinates for item placement
        canvasY: canvasY,
        scale: menuScale,       // Scale factor for the menu
      }
      
      event.preventDefault()
      event.stopPropagation()
    }

    function closeContextMenu() {
      contextMenu.value.visible = false
    }

    function toggleDrawMode() {
      isDrawMode.value = !isDrawMode.value
    }

    function selectDrawing(drawingId) {
      if (!isDrawMode.value) {
        selectedDrawing.value = selectedDrawing.value === drawingId ? null : drawingId
      }
    }

    async function deleteSelectedDrawing() {
      if (selectedDrawing.value) {
        try {
          await api.deleteDrawing(selectedDrawing.value)
          drawings.value = drawings.value.filter(d => d.id !== selectedDrawing.value)
          selectedDrawing.value = null
        } catch (error) {
          console.error('Error deleting drawing:', error)
        }
      }
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

    function handleSvgMouseDown(event) {
      console.log('SVG MouseDown:', {
        isDrawMode: isDrawMode.value,
        button: event.button,
        clientX: event.clientX,
        clientY: event.clientY,
        panX: panX.value,
        panY: panY.value,
        zoom: zoom.value,
        target: event.target.tagName
      })
      
      if (isDrawMode.value && event.button === 0) {
        // Only handle drawing in draw mode with left click
        isDrawing.value = true
        // Convert screen coordinates to canvas coordinates
        const x = (event.clientX - panX.value) / zoom.value
        const y = (event.clientY - 60 - panY.value) / zoom.value  // Subtract toolbar height
        
        console.log('Starting draw at canvas coords:', { x, y })
        
        currentPath.value = [{ x, y }]
        event.stopPropagation()
      }
      // For other cases (not draw mode, or non-left-click), let event bubble to container
    }

    function handleSvgMouseMove(event) {
      if (isDrawing.value && isDrawMode.value) {
        // Only handle drawing movement in draw mode
        const x = (event.clientX - panX.value) / zoom.value
        const y = (event.clientY - 60 - panY.value) / zoom.value  // Subtract toolbar height
        
        if (currentPath.value.length % 10 === 0) {  // Log every 10th point to avoid spam
          console.log('Drawing at:', { x, y, pathLength: currentPath.value.length })
        }
        
        currentPath.value.push({ x, y })
        event.stopPropagation()
      }
      // For other cases, let event bubble to container for pan/drag handling
    }

    async function handleSvgMouseUp(event) {
      if (isDrawing.value && currentPath.value.length > 1) {
        try {
          const pathData = currentPathData.value
          const response = await api.createDrawing({
            whiteboard: whiteboardId.value,
            path_data: pathData,
            color: selectedColor.value,
            stroke_width: 2,
          })
          drawings.value.push(response.data)
          broadcastUpdate({ type: 'drawing_added', drawing: response.data })
        } catch (error) {
          console.error('Error saving drawing:', error)
        }
        currentPath.value = []
        isDrawing.value = false
        event.stopPropagation()
      }
      // For other cases, let event bubble to container
    }

    function updateWhiteboardDimensions() {
      // Keep large fixed dimensions for infinite whiteboard feel
      WHITEBOARD_WIDTH.value = 20000
      WHITEBOARD_HEIGHT.value = 15000
      
      // Initialize view to show existing content or center if no content
      if (canvas.value && zoom.value === 1 && panX.value === 0 && panY.value === 0) {
        const canvasRect = canvas.value.getBoundingClientRect()
        
        if (stickyNotes.value.length > 0) {
          // Calculate the center of existing notes
          const avgX = stickyNotes.value.reduce((sum, note) => sum + note.x, 0) / stickyNotes.value.length
          const avgY = stickyNotes.value.reduce((sum, note) => sum + note.y, 0) / stickyNotes.value.length
          
          // Pan to center the existing content
          panX.value = canvasRect.width / 2 - avgX * zoom.value
          panY.value = canvasRect.height / 2 - avgY * zoom.value
        } else {
          // No content, center the coordinate system
          panX.value = canvasRect.width / 2
          panY.value = canvasRect.height / 2
        }
        
        zoom.value = 1
      }
    }

    onMounted(() => {
      loadWhiteboard()
      loadTextElementsFromLocalStorage()
      setupWebSocket()
      
      // Update dimensions after component is mounted
      setTimeout(updateWhiteboardDimensions, 100)
      
      // Listen for window resize
      window.addEventListener('resize', updateWhiteboardDimensions)
      
      document.addEventListener('click', () => {
        contextMenu.value.visible = false
      })
      
      // Handle paste events for images
      document.addEventListener('paste', async (event) => {
        const items = event.clipboardData?.items
        if (!items) return
        
        for (const item of items) {
          if (item.type.startsWith('image/')) {
            const file = item.getAsFile()
            if (file && selectedNotes.value.length === 1) {
              const note = stickyNotes.value.find(n => n.id === selectedNotes.value[0])
              if (note) {
                const fakeEvent = { target: { files: [file], value: '' } }
                await handleImageUpload(fakeEvent, note)
              }
            }
          }
        }
      })
    })

    onUnmounted(() => {
      window.removeEventListener('resize', updateWhiteboardDimensions)
      if (ws) {
        ws.close()
      }
    })

    return {
      canvas,
      canvasStyle,
      svgStyle,
      panX,
      panY,
      zoom,
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
      handleSvgMouseDown,
      handleSvgMouseMove,
      handleSvgMouseUp,
      handleWheel,
      handleRightClick,
      closeContextMenu,
      toggleDrawMode,
      selectDrawing,
      selectedDrawing,
      deleteSelectedDrawing,
      // Color picker
      showColorPicker,
      availableColors,
      toggleColorPicker,
      changeNoteColor,
      handleImageUpload,
      // Image carousel
      currentImageIndex,
      getCurrentImage,
      nextImage,
      prevImage,
      deleteCurrentImage,
      // Delete confirmation
      showDeleteConfirm,
      confirmDeleteNote,
      cancelDelete,
      confirmDelete,
      // Text elements
      textElements,
      selectedTexts,
      addTextAt,
      getTextStyle,
      selectText,
      handleTextMouseDown,
      handleTextResizeMouseDown,
      updateText,
      confirmDeleteText,
      deleteText,
      // Editing
      editingNote,
      editingText,
      startEditingNote,
      stopEditingNote,
      startEditingText,
      stopEditingText,
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
  overflow: visible;
  background: white;
  margin: 0;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  cursor: default;
}

.toolbar {
  background: #333;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  z-index: 1002;
  position: relative;
  flex-shrink: 0;
  pointer-events: auto;
}

.canvas-area {
  flex: 1;
  position: relative;
  background: white;
  overflow: visible;
  cursor: default;
  min-height: 0;
}

.canvas-area:active {
  cursor: grabbing;
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

.hint-text {
  color: #999;
  font-size: 13px;
  font-style: italic;
  margin-left: 10px;
}

.drawing-layer {
  pointer-events: none;
}

.drawing-layer path {
  pointer-events: auto;
}

.drawing-layer .selected-drawing {
  stroke-width: 4 !important;
  filter: drop-shadow(0 0 4px rgba(0, 123, 255, 0.8));
}

.sticky-note {
  position: absolute;
  border-radius: 0 8px 6px 4px;
  box-shadow: 
    0 4px 8px rgba(0, 0, 0, 0.1),
    0 2px 4px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  display: flex;
  flex-direction: column;
  cursor: move;
  user-select: none;
  transition: all 0.2s ease;
  overflow: hidden;
  pointer-events: auto;
  z-index: 1002;
}

.sticky-note::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 15px;
  height: 15px;
  background: linear-gradient(-45deg, transparent 6px, rgba(0,0,0,0.05) 6px, rgba(0,0,0,0.05) 8px, transparent 8px);
  border-radius: 0 8px 0 0;
}

.sticky-note::after {
  content: '';
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  background: linear-gradient(-45deg, transparent 40%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.1) 60%, transparent 60%);
  border-radius: 0 6px 0 0;
}

.sticky-note:hover {
  box-shadow: 
    0 6px 12px rgba(0, 0, 0, 0.15),
    0 3px 6px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  transform: translate(0, -1px) rotate(var(--rotation, 0deg)) !important;
}

.sticky-note.selected {
  box-shadow: 
    0 0 0 3px #2196f3,
    0 6px 12px rgba(0, 0, 0, 0.15),
    0 3px 6px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.note-header {
  padding: 4px 8px 2px 8px;
  border-radius: 0 8px 0 0;
  display: flex;
  justify-content: flex-end;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.delete-btn {
  background: rgba(0, 0, 0, 0.15);
  border: none;
  color: rgba(0, 0, 0, 0.6);
  font-size: 16px;
  line-height: 1;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: rgba(220, 53, 69, 0.8);
  color: white;
  transform: scale(1.1);
}

.note-content {
  flex: 1;
  padding: 8px 12px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: inherit;
}

.image-carousel {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.image-container {
  position: relative;
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.note-image {
  max-width: 100%;
  max-height: 150px;
  object-fit: contain;
  border-radius: 4px;
}

.carousel-btn {
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  font-size: 24px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
  line-height: 1;
  flex-shrink: 0;
}

.carousel-btn:hover {
  background: rgba(0, 0, 0, 0.7);
  transform: scale(1.1);
}

.delete-image-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(220, 53, 69, 0.8);
  border: none;
  color: white;
  font-size: 16px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0;
}

.image-container:hover .delete-image-btn {
  opacity: 1;
}

.delete-image-btn:hover {
  background: rgba(220, 53, 69, 1);
  transform: scale(1.1);
}

.image-counter {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  pointer-events: none;
}

.note-content textarea {
  flex: 1;
  border: none;
  resize: none;
  font-family: 'Comic Sans MS', 'Marker Felt', cursive, sans-serif;
  font-size: 14px;
  line-height: 1.4;
  outline: none;
  background: transparent;
  color: #333;
  padding: 4px;
  cursor: default;
  user-select: none;
  pointer-events: none;
}

.note-content textarea.editable {
  cursor: text;
  user-select: text;
  pointer-events: auto;
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
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, transparent 50%, rgba(0,0,0,0.1) 50%);
  cursor: nwse-resize;
  border-radius: 0 0 4px 0;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.sticky-note:hover .resize-handle {
  opacity: 1;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  z-index: 10001;
  overflow: hidden;
  min-width: 150px;
  pointer-events: auto;
}

.context-menu div {
  padding: 12px 16px;
  cursor: pointer;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 1px solid #f5f5f5;
  transition: all 0.2s ease;
}

.context-menu div:last-child {
  border-bottom: none;
}

.context-menu div:hover {
  background: #007bff;
  color: white;
}

/* Color picker styles */
.color-btn {
  background: rgba(0, 0, 0, 0.1);
  border: none;
  font-size: 14px;
  width: 24px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-right: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-btn:hover {
  background: rgba(0, 0, 0, 0.2);
}

.image-btn {
  background: rgba(0, 0, 0, 0.1);
  border: none;
  font-size: 14px;
  width: 24px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-right: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-btn:hover {
  background: rgba(0, 0, 0, 0.2);
}

.color-picker {
  position: absolute;
  top: 32px;
  left: 8px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  z-index: 1000;
  padding: 8px;
}

.color-options {
  display: flex;
  gap: 4px;
}

.color-option {
  width: 24px;
  height: 24px;
  border: 2px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-option:hover {
  transform: scale(1.1);
  border-color: #666;
}

.color-option.active {
  border-color: #007bff;
  box-shadow: 0 0 0 1px #007bff;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
}

.modal h3 {
  margin: 0 0 12px 0;
  color: #333;
}

.modal p {
  margin: 0 0 20px 0;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #333;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn:hover {
  background: #f8f9fa;
}

.btn-danger {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}

.btn-danger:hover {
  background: #c82333;
  border-color: #bd2130;
}

/* Text element styles */
.text-element {
  position: absolute;
  min-width: 100px;
  min-height: 30px;
  cursor: move;
  user-select: none;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 4px;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  pointer-events: auto;
  z-index: 1002;
}

.text-element:hover {
  border-color: #ddd;
  background: rgba(255, 255, 255, 0.95);
}

.text-element.selected {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.text-input {
  border: none;
  outline: none;
  background: transparent;
  resize: none;
  width: 100%;
  height: 100%;
  min-height: 20px;
  font-family: Arial, sans-serif;
  line-height: 1.2;
  padding: 0;
  cursor: default;
  user-select: none;
  pointer-events: none;
}

.text-input.editable {
  cursor: text;
  user-select: text;
  pointer-events: auto;
}

.text-delete-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: #dc3545;
  color: white;
  font-size: 12px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.text-element:hover .text-delete-btn {
  display: flex;
}

.text-delete-btn:hover {
  background: #c82333;
  transform: scale(1.1);
}

.text-resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  background: #007bff;
  cursor: nwse-resize;
  border-radius: 0 0 4px 0;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.text-element:hover .text-resize-handle {
  opacity: 1;
}
</style>
