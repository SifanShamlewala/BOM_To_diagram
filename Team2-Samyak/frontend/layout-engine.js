// DeltaV Layout Engine - STRICT GRID SYSTEM
// Professional, clean, no overflow, perfect alignment

const LAYOUT_CONFIG = {
    // Room configuration
    ROOM: {
        PADDING_TOP: 80,      // Space for room name header
        PADDING_SIDES: 40,
        PADDING_BOTTOM: 40,
        MIN_WIDTH: 800,
        MIN_HEIGHT: 900,
        HEADER_HEIGHT: 60,
        GAP_BETWEEN: 150      // Gap between rooms
    },
    
    // Cabinet configuration
    CABINET: {
        WIDTH: 220,           // Fixed width for all cabinets
        MIN_HEIGHT: 700,
        HEADER_HEIGHT: 50,    // Space for cabinet name
        PADDING: 15,
        GAP_BETWEEN: 25       // Gap between cabinets
    },
    
    // Tower configuration (inside IO cabinets)
    TOWER: {
        WIDTH: 48,            // Fixed width per tower column
        GAP: 4,               // Gap between towers
        CIOC_HEIGHT: 45,      // CIOC controller height
        BASEPLATE_HEIGHT: 35, // Baseplate height
        ITEM_GAP: 5          // Gap between items
    },
    
    // Device configuration (inside Server/Workdesk cabinets)
    DEVICE: {
        WIDTH: 190,           // Fits inside cabinet (220 - 2*15 padding)
        HEIGHT: 45,
        GAP: 8                // Gap between devices
    },
    
    // Controller configuration
    CONTROLLER: {
        WIDTH: 190,
        HEIGHT: 50,
        GAP: 8
    },
    
    // FOPP configuration
    FOPP: {
        WIDTH: 100,
        HEIGHT: 70
    }
};

class GridLayoutEngine {
    constructor(bomData) {
        this.bomData = bomData;
        this.shapes = [];
        this.shapeIdCounter = 0;
    }
    
    generate() {
        this.shapes = [];
        this.shapeIdCounter = 0;
        
        let roomX = 50; // Start position
        
        this.bomData.rooms.forEach((room, roomIndex) => {
            try {
                console.log('[LayoutEngine] Processing room:', room.room_type, '| controllers:', (room.controllers||[]).length, '| devices:', (room.devices||[]).length, '| baseplates:', room.baseplates);
                const roomLayout = this.layoutRoom(room, roomX, 50);
                roomX += roomLayout.width + LAYOUT_CONFIG.ROOM.GAP_BETWEEN;
            } catch(err) {
                console.error('[LayoutEngine] CRASH on room', room.room_type, ':', err.message, err.stack);
            }
        });
        
        return this.shapes;
    }
    
    layoutRoom(room, x, y) {
        const cfg = LAYOUT_CONFIG.ROOM;
        
        // Calculate how many cabinets we need
        const cabinets = [];
        
        // Step 1: Start with BOM-derived SRV-01 cabinet (controllers/devices with no _cabinetLabel)
        const defaultControllers = (room.controllers || []).filter(c => !c._cabinetLabel);
        const defaultDevices = (room.devices || []).filter(d => !d._cabinetLabel);
        if (defaultControllers.length > 0 || defaultDevices.length > 0) {
            cabinets.push({ type: 'SERVER', label: 'SRV-01', controllers: defaultControllers, devices: defaultDevices });
        }

        // Step 2: Add manually-created cabinets (extraCabinets), slotting in any
        // controllers/devices that are tagged with matching _cabinetLabel
        (room.extraCabinets || []).forEach(cab => {
            const taggedControllers = (room.controllers || []).filter(c => c._cabinetLabel === cab.label);
            const taggedDevices = (room.devices || []).filter(d => d._cabinetLabel === cab.label);
            cabinets.push({
                type: 'SERVER',
                label: cab.label,
                controllers: taggedControllers,
                devices: taggedDevices
            });
        });

        // IO cabinets (for baseplates)
        if (room.baseplates > 0) {
            const baseplatesPerTower = 8;
            const towersPerCabinet = 4;
            const numIOCabinets = Math.ceil(room.baseplates / (baseplatesPerTower * towersPerCabinet));
            
            for (let i = 0; i < numIOCabinets; i++) {
                cabinets.push({
                    type: 'IO',
                    label: `IO-${String(i + 1).padStart(2, '0')}`,
                    cabinetIndex: i,
                    totalBaseplates: room.baseplates
                });
            }
        }
        
        // Calculate room dimensions
        const numCabinets = cabinets.length;
        const roomWidth = Math.max(
            cfg.MIN_WIDTH,
            cfg.PADDING_SIDES * 2 + 
            numCabinets * LAYOUT_CONFIG.CABINET.WIDTH + 
            (numCabinets - 1) * LAYOUT_CONFIG.CABINET.GAP_BETWEEN +
            (room.fopp_count > 0 ? 130 : 0) // Extra space for FOPP
        );
        const roomHeight = cfg.MIN_HEIGHT;
        
        // Add room shape
        const roomShape = this.addShape({
            type: 'room',
            label: room.room_type,
            x: x,
            y: y,
            width: roomWidth,
            height: roomHeight,
            properties: { room_type: room.room_type }
        });
        
        // Layout cabinets inside room
        let cabinetX = x + cfg.PADDING_SIDES;
        const cabinetY = y + cfg.PADDING_TOP;
        
        cabinets.forEach(cabinet => {
            if (cabinet.type === 'SERVER') {
                this.layoutServerCabinet(cabinet, cabinetX, cabinetY, roomShape.id);
            } else if (cabinet.type === 'IO') {
                this.layoutIOCabinet(cabinet, cabinetX, cabinetY, roomShape.id);
            }
            
            cabinetX += LAYOUT_CONFIG.CABINET.WIDTH + LAYOUT_CONFIG.CABINET.GAP_BETWEEN;
        });
        
        // Add FOPP if exists
        if (room.fopp_count > 0) {
            this.addShape({
                type: 'fopp',
                label: 'FOPP',
                x: x + roomWidth - cfg.PADDING_SIDES - LAYOUT_CONFIG.FOPP.WIDTH,
                y: y + roomHeight - cfg.PADDING_BOTTOM - LAYOUT_CONFIG.FOPP.HEIGHT,
                width: LAYOUT_CONFIG.FOPP.WIDTH,
                height: LAYOUT_CONFIG.FOPP.HEIGHT,
                parentId: roomShape.id,
                properties: {}
            });
        }
        
        return { width: roomWidth, height: roomHeight };
    }
    
    layoutServerCabinet(cabinet, x, y, parentId) {
        const cfg = LAYOUT_CONFIG.CABINET;
        
        // Calculate cabinet height
        const numControllers = cabinet.controllers.length;
        const numDevices = cabinet.devices.length;
        
        const contentHeight = 
            cfg.HEADER_HEIGHT +
            numControllers * (LAYOUT_CONFIG.CONTROLLER.HEIGHT + LAYOUT_CONFIG.CONTROLLER.GAP) +
            numDevices * (LAYOUT_CONFIG.DEVICE.HEIGHT + LAYOUT_CONFIG.DEVICE.GAP) +
            cfg.PADDING * 2;
        
        const cabinetHeight = Math.max(cfg.MIN_HEIGHT, contentHeight);
        
        // Add cabinet shape
        const cabinetShape = this.addShape({
            type: 'cabinet',
            label: cabinet.label,
            x: x,
            y: y,
            width: cfg.WIDTH,
            height: cabinetHeight,
            parentId: parentId,
            properties: { cabinet_type: 'server' }
        });
        
        // Layout contents
        let itemY = y + cfg.HEADER_HEIGHT + cfg.PADDING;
        const itemX = x + cfg.PADDING;
        
        // Controllers
        cabinet.controllers.forEach(ctrl => {
            this.addShape({
                type: 'controller',
                label: ctrl.label || ctrl.id,
                x: itemX,
                y: itemY,
                width: LAYOUT_CONFIG.CONTROLLER.WIDTH,
                height: LAYOUT_CONFIG.CONTROLLER.HEIGHT,
                parentId: cabinetShape.id,
                properties: ctrl
            });
            itemY += LAYOUT_CONFIG.CONTROLLER.HEIGHT + LAYOUT_CONFIG.CONTROLLER.GAP;
        });
        
        // Devices
        cabinet.devices.forEach(dev => {
            this.addShape({
                type: 'device',
                label: dev.label,
                x: itemX,
                y: itemY,
                width: LAYOUT_CONFIG.DEVICE.WIDTH,
                height: LAYOUT_CONFIG.DEVICE.HEIGHT,
                parentId: cabinetShape.id,
                properties: dev
            });
            itemY += LAYOUT_CONFIG.DEVICE.HEIGHT + LAYOUT_CONFIG.DEVICE.GAP;
        });
    }
    
    layoutIOCabinet(cabinet, x, y, parentId) {
        const cfg = LAYOUT_CONFIG.CABINET;
        const towerCfg = LAYOUT_CONFIG.TOWER;
        
        const baseplatesPerTower = 8;
        const towersPerCabinet = 4;
        
        const cabinetStartBP = cabinet.cabinetIndex * baseplatesPerTower * towersPerCabinet;
        const cabinetEndBP = Math.min(
            cabinetStartBP + (baseplatesPerTower * towersPerCabinet),
            cabinet.totalBaseplates
        );
        const bpsInCabinet = cabinetEndBP - cabinetStartBP;
        const numTowers = Math.ceil(bpsInCabinet / baseplatesPerTower);
        
        // Calculate cabinet height
        const towerHeight = 
            towerCfg.CIOC_HEIGHT + 
            towerCfg.ITEM_GAP +
            baseplatesPerTower * (towerCfg.BASEPLATE_HEIGHT + towerCfg.ITEM_GAP);
        
        const cabinetHeight = Math.max(
            cfg.MIN_HEIGHT,
            cfg.HEADER_HEIGHT + cfg.PADDING * 2 + towerHeight
        );
        
        // Add cabinet shape
        const cabinetShape = this.addShape({
            type: 'cabinet',
            label: cabinet.label,
            x: x,
            y: y,
            width: cfg.WIDTH,
            height: cabinetHeight,
            parentId: parentId,
            properties: { cabinet_type: 'io' }
        });
        
        // Layout towers
        const totalTowerWidth = numTowers * towerCfg.WIDTH + (numTowers - 1) * towerCfg.GAP;
        let towerX = x + (cfg.WIDTH - totalTowerWidth) / 2; // Center towers
        
        for (let t = 0; t < numTowers; t++) {
            const towerStartBP = cabinetStartBP + t * baseplatesPerTower;
            const towerEndBP = Math.min(towerStartBP + baseplatesPerTower, cabinetEndBP);
            const bpsInTower = towerEndBP - towerStartBP;
            
            this.layoutTower(
                towerX,
                y + cfg.HEADER_HEIGHT + cfg.PADDING,
                towerStartBP,
                bpsInTower,
                cabinet.cabinetIndex * towersPerCabinet + t,
                cabinetShape.id
            );
            
            towerX += towerCfg.WIDTH + towerCfg.GAP;
        }
    }
    
    layoutTower(x, y, startBP, numBPs, towerIndex, parentId) {
        const towerCfg = LAYOUT_CONFIG.TOWER;
        
        let itemY = y;
        
        // CIOC at top
        const ciocNum = towerIndex + 1;
        this.addShape({
            type: 'controller',
            label: `CIOC-${String(ciocNum).padStart(2, '0')}`,
            x: x,
            y: itemY,
            width: towerCfg.WIDTH,
            height: towerCfg.CIOC_HEIGHT,
            parentId: parentId,
            properties: { cioc: true }
        });
        itemY += towerCfg.CIOC_HEIGHT + towerCfg.ITEM_GAP;
        
        // Baseplates
        for (let bp = 0; bp < numBPs; bp++) {
            const bpNum = startBP + bp + 1;
            this.addShape({
                type: 'baseplate',
                label: `BP-${bpNum}`,
                x: x,
                y: itemY,
                width: towerCfg.WIDTH,
                height: towerCfg.BASEPLATE_HEIGHT,
                parentId: parentId,
                properties: { bp_number: bpNum }
            });
            itemY += towerCfg.BASEPLATE_HEIGHT + towerCfg.ITEM_GAP;
        }
    }
    
    addShape(config) {
        const id = `shape-${this.shapeIdCounter++}`;
        const shape = {
            id,
            type: config.type,
            label: config.label,
            x: config.x,
            y: config.y,
            width: config.width,
            height: config.height,
            parentId: config.parentId || null,
            properties: config.properties || {}
        };
        
        this.shapes.push(shape);
        return shape;
    }
}

// Export for use
window.GridLayoutEngine = GridLayoutEngine;
window.LAYOUT_CONFIG = LAYOUT_CONFIG;