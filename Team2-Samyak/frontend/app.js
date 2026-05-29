// DeltaV Architecture Editor - GRID-BASED, NO FLICKERING

const API_URL = 'http://localhost:8000';

let shapes = [];
let selectedShape = null;
let bomData = null;

// DOM Elements
const uploadOverlay = document.getElementById('uploadOverlay');
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const exportBtn = document.getElementById('exportBtn');
const shapesContainer = document.getElementById('shapesContainer');
const componentList = document.getElementById('componentList');
const componentCount = document.getElementById('componentCount');

const addRoomBtn = document.getElementById('addRoomBtn');
const addCabinetBtn = document.getElementById('addCabinetBtn');
const addControllerBtn = document.getElementById('addControllerBtn');
const deleteBtn = document.getElementById('deleteBtn');

const addRoomModal = document.getElementById('addRoomModal');
const addCabinetModal = document.getElementById('addCabinetModal');
const addControllerModal = document.getElementById('addControllerModal');

// Upload handling
uploadBtn.addEventListener('click', () => {
    uploadOverlay.classList.remove('hidden');
});

uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#764ba2';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#667eea';
    if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
});

async function handleFileUpload(file) {
    if (!file.name.match(/\.xlsx?$/i)) {
        showStatus('Please upload an Excel file', 'error');
        return;
    }

    uploadArea.innerHTML = '<div style="font-size: 40px;">⏳</div><div style="margin-top: 12px;">Parsing BOM...</div>';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/api/parse-bom`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to parse BOM');

        const result = await response.json();
        bomData = result.data;
        
        generateShapesFromBOM(bomData);
        uploadOverlay.classList.add('hidden');
        
        exportBtn.disabled = false;
        addRoomBtn.disabled = false;
        addCabinetBtn.disabled = false;
        addControllerBtn.disabled = false;
        
        showStatus('✅ BOM loaded!');
        uploadArea.innerHTML = '<div class="upload-icon">📊</div><div style="font-size: 1.1rem; margin-bottom: 8px;">Click or drag & drop</div><div style="color: #9ca3af; font-size: 0.9rem;">Excel files (.xlsx, .xls)</div>';
        
    } catch (error) {
        console.error(error);
        showStatus('❌ Error: ' + error.message, 'error');
        uploadArea.innerHTML = '<div class="upload-icon">📊</div><div style="font-size: 1.1rem; margin-bottom: 8px;">Click or drag & drop</div><div style="color: #9ca3af; font-size: 0.9rem;">Excel files (.xlsx, .xls)</div>';
    }
}

// Use Grid Layout Engine
function generateShapesFromBOM(data) {
    shapes = [];
    shapesContainer.innerHTML = '';
    
    try {
        console.log('[generateShapesFromBOM] bomData rooms:', JSON.stringify(data.rooms.map(r => ({room_type: r.room_type, controllers: r.controllers?.length, devices: r.devices?.length, baseplates: r.baseplates}))));
        const layoutEngine = new GridLayoutEngine(data);
        shapes = layoutEngine.generate();
        console.log('[generateShapesFromBOM] Generated shapes:', shapes.length);
        shapes.forEach(shape => renderShape(shape));
        updateComponentList();
    } catch(err) {
        console.error('[generateShapesFromBOM] CRASH:', err.message, err.stack);
        showStatus('Layout error: ' + err.message, 'error');
    }
}

function renderShape(shape) {
    const elem = document.createElement('div');
    elem.id = shape.id;
    elem.className = `shape shape-${shape.type}`;
    
    if (shape.type === 'cabinet' && shape.properties.cabinet_type) {
        elem.classList.add(shape.properties.cabinet_type);
    }
    
    // Create header for rooms and cabinets
    if (shape.type === 'room' || shape.type === 'cabinet') {
        const header = document.createElement('div');
        header.className = 'shape-header';
        const dragHint = (shape.type === 'cabinet') ? ' <span class="drag-hint" title="Drag to move to another room">⠿</span>' : '';
        header.innerHTML = `
            <div class="shape-label">${shape.label}${dragHint}</div>
            <div class="shape-type">${shape.type}</div>
        `;
        elem.appendChild(header);
        
        const body = document.createElement('div');
        body.className = 'shape-body';
        elem.appendChild(body);
    } else {
        // Simple label for devices/controllers
        const dragHint2 = (shape.type === 'controller') ? '<span class="drag-hint" title="Drag to move to another cabinet">⠿</span> ' : '';
        elem.innerHTML = `
            <div class="shape-label">${dragHint2}${shape.label}</div>
        `;
    }
    
    elem.style.left = shape.x + 'px';
    elem.style.top = shape.y + 'px';
    if (shape.width) elem.style.width = shape.width + 'px';
    if (shape.height) elem.style.height = shape.height + 'px';

    shapesContainer.appendChild(elem);

    // Make draggable - smart drag for cabinets and controllers
    interact(`#${shape.id}`)
        .draggable({
            inertia: false,
            modifiers: [
                interact.modifiers.snap({
                    targets: [interact.snappers.grid({ x: 20, y: 20 })],
                    range: Infinity,
                    relativePoints: [{ x: 0, y: 0 }]
                })
            ],
            listeners: {
                start: dragStartListener,
                move: dragMoveListener,
                end: dragEndListener
            }
        })
        .on('tap', function() {
            selectShape(shape.id);
        });
}

// Track drag state
let draggingShape = null;
let dragHighlightedTarget = null;

function dragStartListener(event) {
    const shapeId = event.target.id;
    draggingShape = shapes.find(s => s.id === shapeId);
    if (draggingShape) {
        event.target.style.zIndex = '9999';
        event.target.style.opacity = '0.85';
        event.target.style.boxShadow = '0 8px 32px rgba(0,0,0,0.25)';
    }
}

function dragMoveListener(event) {
    const target = event.target;
    const shapeId = target.id;
    const shape = shapes.find(s => s.id === shapeId);
    if (!shape) return;

    shape.x += event.dx;
    shape.y += event.dy;
    target.style.left = shape.x + 'px';
    target.style.top = shape.y + 'px';

    // Highlight valid drop target
    if (shape.type === 'cabinet' || shape.type === 'controller') {
        const targetType = shape.type === 'cabinet' ? 'room' : 'cabinet';
        const dropTarget = findDropTarget(shape, targetType);

        if (dragHighlightedTarget && dragHighlightedTarget !== dropTarget) {
            document.getElementById(dragHighlightedTarget.id)?.classList.remove('drop-target-highlight');
            dragHighlightedTarget = null;
        }
        if (dropTarget) {
            document.getElementById(dropTarget.id)?.classList.add('drop-target-highlight');
            dragHighlightedTarget = dropTarget;
        }
    }
}

function dragEndListener(event) {
    const target = event.target;
    const shapeId = target.id;
    const shape = shapes.find(s => s.id === shapeId);

    // Reset visual
    target.style.zIndex = '';
    target.style.opacity = '';
    target.style.boxShadow = '';

    // Clear highlight
    if (dragHighlightedTarget) {
        document.getElementById(dragHighlightedTarget.id)?.classList.remove('drop-target-highlight');
        dragHighlightedTarget = null;
    }

    if (!shape) { draggingShape = null; return; }

    // Smart drop: cabinet onto room, or controller onto cabinet
    if (shape.type === 'cabinet') {
        const targetRoom = findDropTarget(shape, 'room');
        if (targetRoom && targetRoom.id !== shape.parentId) {
            reparentShape(shape, targetRoom);
            return;
        }
    } else if (shape.type === 'controller') {
        const targetCabinet = findDropTarget(shape, 'cabinet');
        if (targetCabinet && targetCabinet.id !== shape.parentId) {
            reparentShape(shape, targetCabinet);
            return;
        }
    }

    draggingShape = null;
}

function getShapeCenter(shape) {
    return {
        x: shape.x + (shape.width || 100) / 2,
        y: shape.y + (shape.height || 50) / 2
    };
}

function shapesOverlap(a, b) {
    const aw = a.width || 100, ah = a.height || 50;
    const bw = b.width || 100, bh = b.height || 50;
    return !(a.x + aw < b.x || b.x + bw < a.x ||
             a.y + ah < b.y || b.y + bh < a.y);
}

function findDropTarget(shape, targetType) {
    // Find the best overlapping target of given type (excluding self and current parent)
    let best = null;
    let bestArea = 0;

    shapes.forEach(candidate => {
        if (candidate.id === shape.id) return;
        if (candidate.type !== targetType) return;
        if (!shapesOverlap(shape, candidate)) return;

        // Pick the one with most overlap
        const aw = shape.width || 100, ah = shape.height || 50;
        const bw = candidate.width || 100, bh = candidate.height || 50;
        const ox = Math.min(shape.x + aw, candidate.x + bw) - Math.max(shape.x, candidate.x);
        const oy = Math.min(shape.y + ah, candidate.y + bh) - Math.max(shape.y, candidate.y);
        const area = ox * oy;
        if (area > bestArea) { bestArea = area; best = candidate; }
    });

    return best;
}

function reparentShape(shape, newParent) {
    const oldParentId = shape.parentId;
    const oldParent = shapes.find(s => s.id === oldParentId);

    // Update bomData to reflect the move
    if (shape.type === 'cabinet' && newParent.type === 'room') {
        // Remove cabinet's controllers/devices from old room, add to new room
        moveCabinetInBomData(shape, oldParent, newParent);
    } else if (shape.type === 'controller' && newParent.type === 'cabinet') {
        moveControllerInBomData(shape, oldParent, newParent);
    }

    // Regenerate layout
    const newParentLabel = newParent.label;
    const shapeLabel = shape.label;
    generateShapesFromBOM(bomData);

    // Re-select the moved shape
    const restored = shapes.find(s => s.label === shapeLabel &&
        (s.type === 'cabinet' || s.type === 'controller') &&
        shapes.find(p => p.id === s.parentId && p.label === newParentLabel));
    if (restored) selectShape(restored.id);

    showStatus('Moved "' + shapeLabel + '" to "' + newParentLabel + '"');
    draggingShape = null;
}

function moveCabinetInBomData(cabinetShape, oldRoomShape, newRoomShape) {
    if (!bomData) return;

    const oldRoom = oldRoomShape ? bomData.rooms.find(r => r.room_type === oldRoomShape.label) : null;
    const newRoom = bomData.rooms.find(r => r.room_type === newRoomShape.label);
    if (!newRoom) return;

    const cabinetLabel = cabinetShape.label;

    // Move any controllers/devices belonging to this cabinet
    const movedControllers = (oldRoom?.controllers || []).filter(c => c._cabinetLabel === cabinetLabel || (!c._cabinetLabel && cabinetLabel === 'SRV-01'));
    const movedDevices = (oldRoom?.devices || []).filter(d => d._cabinetLabel === cabinetLabel || (!d._cabinetLabel && cabinetLabel === 'SRV-01'));

    if (oldRoom) {
        oldRoom.controllers = (oldRoom.controllers || []).filter(c => !movedControllers.includes(c));
        oldRoom.devices = (oldRoom.devices || []).filter(d => !movedDevices.includes(d));
    }

    if (!newRoom.controllers) newRoom.controllers = [];
    if (!newRoom.devices) newRoom.devices = [];
    movedControllers.forEach(c => { c._cabinetLabel = cabinetLabel; newRoom.controllers.push(c); });
    movedDevices.forEach(d => { d._cabinetLabel = cabinetLabel; newRoom.devices.push(d); });

    // Also move extraCabinets entry if it exists
    if (oldRoom?.extraCabinets) {
        const idx = oldRoom.extraCabinets.findIndex(c => c.label === cabinetLabel);
        if (idx !== -1) {
            const [cab] = oldRoom.extraCabinets.splice(idx, 1);
            if (!newRoom.extraCabinets) newRoom.extraCabinets = [];
            newRoom.extraCabinets.push(cab);
        }
    }
}

function moveControllerInBomData(controllerShape, oldCabinetShape, newCabinetShape) {
    if (!bomData) return;

    const oldCabinetParent = oldCabinetShape ? shapes.find(s => s.id === oldCabinetShape.parentId) : null;
    const newCabinetParent = shapes.find(s => s.id === newCabinetShape.parentId);
    if (!newCabinetParent) return;

    const oldRoom = oldCabinetParent ? bomData.rooms.find(r => r.room_type === oldCabinetParent.label) : null;
    const newRoom = bomData.rooms.find(r => r.room_type === newCabinetParent.label);
    if (!newRoom) return;

    const ctrlLabel = controllerShape.label;
    const oldCabLabel = oldCabinetShape?.label;

    // Find the controller in old room
    const ctrl = (oldRoom?.controllers || []).find(c =>
        (c.label === ctrlLabel || c.id === ctrlLabel) &&
        (c._cabinetLabel === oldCabLabel || (!c._cabinetLabel && oldCabLabel === 'SRV-01'))
    );

    if (ctrl) {
        // Remove from old room
        if (oldRoom) oldRoom.controllers = oldRoom.controllers.filter(c => c !== ctrl);
        // Add to new room with new cabinet label
        if (!newRoom.controllers) newRoom.controllers = [];
        ctrl._cabinetLabel = newCabinetShape.label;
        newRoom.controllers.push(ctrl);
    } else {
        // Fallback: create new entry
        if (!newRoom.controllers) newRoom.controllers = [];
        newRoom.controllers.push({
            id: 'CNTR-' + ctrlLabel + '-' + Date.now(),
            label: ctrlLabel,
            type: 'controller',
            _cabinetLabel: newCabinetShape.label
        });
    }
}

function selectShape(id) {
    document.querySelectorAll('.shape').forEach(s => s.classList.remove('selected'));
    document.querySelectorAll('.component-item').forEach(c => c.classList.remove('selected'));
    
    const elem = document.getElementById(id);
    if (elem) {
        elem.classList.add('selected');
        selectedShape = shapes.find(s => s.id === id);
        deleteBtn.disabled = false;
        
        const sidebarItem = document.querySelector(`[data-shape-id="${id}"]`);
        if (sidebarItem) {
            sidebarItem.classList.add('selected');
            sidebarItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        updateButtonStates();
    }
}

function updateButtonStates() {
    if (!selectedShape) {
        addCabinetBtn.disabled = true;
        addControllerBtn.disabled = true;
        deleteBtn.disabled = true;
        return;
    }
    
    addCabinetBtn.disabled = selectedShape.type !== 'room';
    addControllerBtn.disabled = selectedShape.type !== 'cabinet';
}

function updateComponentList() {
    const roomCount = shapes.filter(s => s.type === 'room').length;
    const totalCount = shapes.length;
    
    componentCount.textContent = `${roomCount} rooms, ${totalCount} total components`;
    
    componentList.innerHTML = '';
    
    shapes.forEach(shape => {
        const item = document.createElement('div');
        item.className = 'component-item';
        item.setAttribute('data-shape-id', shape.id);
        item.innerHTML = `
            <div class="component-label">${shape.label}</div>
            <div class="component-type">${shape.type}</div>
        `;
        
        item.addEventListener('click', () => {
            selectShape(shape.id);
            const elem = document.getElementById(shape.id);
            if (elem) {
                elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        
        componentList.appendChild(item);
    });
}

// Add Room - same as before
addRoomBtn.addEventListener('click', () => {
    addRoomModal.classList.remove('hidden');
    document.getElementById('roomName').value = '';
    document.getElementById('roomName').focus();
});

document.getElementById('cancelRoomBtn').addEventListener('click', () => {
    addRoomModal.classList.add('hidden');
});

document.getElementById('confirmRoomBtn').addEventListener('click', () => {
    const name = document.getElementById('roomName').value.trim();
    if (!name) {
        showStatus('Please enter a room name', 'error');
        return;
    }
    
    // Add to bomData and regenerate
    bomData.rooms.push({
        room_type: name,
        controllers: [],
        baseplates: 0,
        fopp_count: 0,
        devices: []
    });
    
    generateShapesFromBOM(bomData);
    addRoomModal.classList.add('hidden');
    showStatus(`✅ Room "${name}" added!`);
});

// Add Cabinet - same as before
addCabinetBtn.addEventListener('click', () => {
    if (!selectedShape || selectedShape.type !== 'room') {
        showStatus('Please select a room first', 'error');
        return;
    }
    
    addCabinetModal.classList.remove('hidden');
    document.getElementById('cabinetName').value = '';
    document.getElementById('cabinetType').value = 'server';
    document.getElementById('cabinetName').focus();
});

document.getElementById('cancelCabinetBtn').addEventListener('click', () => {
    addCabinetModal.classList.add('hidden');
});

document.getElementById('confirmCabinetBtn').addEventListener('click', () => {
    const name = document.getElementById('cabinetName').value.trim();
    const type = document.getElementById('cabinetType').value;

    if (!name) {
        showStatus('Please enter a cabinet name', 'error');
        return;
    }

    if (!selectedShape || selectedShape.type !== 'room') {
        showStatus('Please select a room first', 'error');
        return;
    }

    // Snapshot before generateShapesFromBOM clears state
    const roomLabel = selectedShape.label;

    const targetRoom = bomData.rooms.find(r => r.room_type === roomLabel);
    if (!targetRoom) {
        showStatus('Could not find room "' + roomLabel + '" in data', 'error');
        return;
    }

    // Store cabinet in its own list — NOT in controllers
    if (!targetRoom.extraCabinets) targetRoom.extraCabinets = [];
    targetRoom.extraCabinets.push({
        id: 'CAB-' + name + '-' + Date.now(),
        label: name,
        cabinet_type: type  // 'server' or 'io'
    });

    addCabinetModal.classList.add('hidden');
    generateShapesFromBOM(bomData);

    const restoredRoom = shapes.find(s => s.type === 'room' && s.label === roomLabel);
    if (restoredRoom) selectShape(restoredRoom.id);
    showStatus('Cabinet "' + name + '" added to ' + roomLabel + '!');
});

// Add Controller - same as before  
addControllerBtn.addEventListener('click', () => {
    if (!selectedShape || selectedShape.type !== 'cabinet') {
        showStatus('Please select a cabinet first', 'error');
        return;
    }
    
    addControllerModal.classList.remove('hidden');
    document.getElementById('controllerName').value = '';
    document.getElementById('controllerName').focus();
});

document.getElementById('cancelControllerBtn').addEventListener('click', () => {
    addControllerModal.classList.add('hidden');
});

document.getElementById('confirmControllerBtn').addEventListener('click', () => {
    const name = document.getElementById('controllerName').value.trim();

    if (!name) {
        showStatus('Please enter a controller name', 'error');
        return;
    }

    if (!selectedShape || selectedShape.type !== 'cabinet') {
        showStatus('Please select a cabinet first', 'error');
        return;
    }

    // Snapshot before regeneration
    const cabinetLabel = selectedShape.label;
    const cabinetParentId = selectedShape.parentId;

    const parentRoom = shapes.find(s => s.id === cabinetParentId && s.type === 'room');
    if (!parentRoom) {
        showStatus('Could not find parent room for cabinet', 'error');
        return;
    }

    const parentRoomLabel = parentRoom.label;
    const targetRoom = bomData.rooms.find(r => r.room_type === parentRoomLabel);
    if (!targetRoom) {
        showStatus('Could not find room "' + parentRoomLabel + '" in data', 'error');
        return;
    }

    if (!targetRoom.controllers) targetRoom.controllers = [];

    // Add controller tagged to this cabinet so it renders inside it
    targetRoom.controllers.push({
        id: 'CNTR-' + name + '-' + Date.now(),
        label: name,
        type: 'controller',
        _cabinetLabel: cabinetLabel
    });

    addControllerModal.classList.add('hidden');
    generateShapesFromBOM(bomData);

    // Re-select the same cabinet after regeneration
    const restoredCabinet = shapes.find(s => s.type === 'cabinet' && s.label === cabinetLabel);
    if (restoredCabinet) selectShape(restoredCabinet.id);
    else {
        const restoredRoom = shapes.find(s => s.type === 'room' && s.label === parentRoomLabel);
        if (restoredRoom) selectShape(restoredRoom.id);
    }
    showStatus(`✅ Controller "${name}" added!`);
});

// Delete
deleteBtn.addEventListener('click', () => {
    if (!selectedShape) return;
    
    if (confirm(`Delete "${selectedShape.label}"?`)) {
        const elem = document.getElementById(selectedShape.id);
        if (elem) elem.remove();
        
        shapes = shapes.filter(s => s.id !== selectedShape.id);
        
        selectedShape = null;
        deleteBtn.disabled = true;
        updateComponentList();
        showStatus('✅ Deleted');
    }
});

// Export to PPT
exportBtn.addEventListener('click', async () => {
    if (shapes.length === 0) {
        showStatus('No shapes to export!', 'error');
        return;
    }

    showStatus('Exporting to PowerPoint...');
    exportBtn.disabled = true;
    exportBtn.textContent = '⏳ Exporting...';

    try {
        const response = await fetch(`${API_URL}/api/export-ppt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                shapes: shapes,
                connections: []
            })
        });

        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'deltav_architecture.pptx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showStatus('✅ PowerPoint exported!');
        exportBtn.textContent = '💾 Export PPT';
        exportBtn.disabled = false;

    } catch (error) {
        console.error(error);
        showStatus('❌ Export failed', 'error');
        exportBtn.textContent = '💾 Export PPT';
        exportBtn.disabled = false;
    }
});

function showStatus(message, type = 'success') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status show';
    if (type === 'error') status.classList.add('error');
    
    setTimeout(() => {
        status.classList.remove('show');
    }, 3000);
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Delete' && selectedShape) {
        deleteBtn.click();
    }
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay').forEach(m => m.classList.add('hidden'));
    }
});