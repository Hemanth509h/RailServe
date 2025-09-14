/**
 * RailServe 3D Hero Animation
 * Features a procedural train moving on rails with sky gradient background
 */

let scene, camera, renderer, train, rails;
let animationId = null;
let isAnimating = false;
let canvas = null;

// Animation settings
const TRAIN_SPEED = 0.02;
const RAIL_LENGTH = 20;
const TRAIN_POSITION_RANGE = RAIL_LENGTH;

function init3DHero() {
    canvas = document.getElementById('hero3d');
    if (!canvas) return false;

    // Check WebGL support
    if (!window.WebGLRenderingContext) {
        console.log('WebGL not supported, falling back to regular hero');
        return false;
    }

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const stored3DPreference = localStorage.getItem('railserve-3d-enabled');
    
    if (prefersReducedMotion && stored3DPreference === null) {
        // Default to disabled if user prefers reduced motion
        localStorage.setItem('railserve-3d-enabled', 'false');
        canvas.style.display = 'none';
        return false;
    }

    if (stored3DPreference === 'false') {
        canvas.style.display = 'none';
        return false;
    }

    try {
        // Initialize Three.js
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
        renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        
        renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Cap for performance
        
        // Sky gradient background
        scene.fog = new THREE.Fog(0x87CEEB, 20, 100);
        
        // Camera position
        camera.position.set(0, 3, 8);
        camera.lookAt(0, 0, 0);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        scene.add(directionalLight);
        
        // Create rails
        createRails();
        
        // Create train
        createTrain();
        
        // Start animation
        animate();
        isAnimating = true;
        
        return true;
    } catch (error) {
        console.error('3D initialization failed:', error);
        canvas.style.display = 'none';
        return false;
    }
}

function createRails() {
    const railGroup = new THREE.Group();
    
    // Rail geometry
    const railGeometry = new THREE.BoxGeometry(0.1, 0.1, RAIL_LENGTH);
    const railMaterial = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
    
    // Left rail
    const leftRail = new THREE.Mesh(railGeometry, railMaterial);
    leftRail.position.set(-0.7, -0.5, 0);
    railGroup.add(leftRail);
    
    // Right rail
    const rightRail = new THREE.Mesh(railGeometry, railMaterial);
    rightRail.position.set(0.7, -0.5, 0);
    railGroup.add(rightRail);
    
    // Railway ties
    const tieGeometry = new THREE.BoxGeometry(2, 0.1, 0.2);
    const tieMaterial = new THREE.MeshLambertMaterial({ color: 0x654321 });
    
    for (let i = -RAIL_LENGTH/2; i < RAIL_LENGTH/2; i += 1) {
        const tie = new THREE.Mesh(tieGeometry, tieMaterial);
        tie.position.set(0, -0.55, i);
        railGroup.add(tie);
    }
    
    rails = railGroup;
    scene.add(rails);
}

function createTrain() {
    const trainGroup = new THREE.Group();
    
    // Train body
    const bodyGeometry = new THREE.BoxGeometry(1.2, 0.8, 2.5);
    const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x1E90FF });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.set(0, 0.4, 0);
    trainGroup.add(body);
    
    // Train roof
    const roofGeometry = new THREE.BoxGeometry(1.3, 0.1, 2.6);
    const roofMaterial = new THREE.MeshLambertMaterial({ color: 0x4169E1 });
    const roof = new THREE.Mesh(roofGeometry, roofMaterial);
    roof.position.set(0, 0.85, 0);
    trainGroup.add(roof);
    
    // Front of train (locomotive front)
    const frontGeometry = new THREE.BoxGeometry(0.8, 0.6, 0.5);
    const frontMaterial = new THREE.MeshLambertMaterial({ color: 0xFF4500 });
    const front = new THREE.Mesh(frontGeometry, frontMaterial);
    front.position.set(0, 0.3, 1.5);
    trainGroup.add(front);
    
    // Wheels
    const wheelGeometry = new THREE.CylinderGeometry(0.2, 0.2, 0.1);
    const wheelMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
    
    const wheelPositions = [
        [-0.5, -0.1, -0.8], [0.5, -0.1, -0.8],
        [-0.5, -0.1, 0.8], [0.5, -0.1, 0.8]
    ];
    
    wheelPositions.forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        wheel.position.set(pos[0], pos[1], pos[2]);
        wheel.rotation.z = Math.PI / 2;
        trainGroup.add(wheel);
    });
    
    // Initial position
    trainGroup.position.z = -TRAIN_POSITION_RANGE / 2;
    train = trainGroup;
    scene.add(train);
}

function animate() {
    if (!isAnimating) return;
    
    animationId = requestAnimationFrame(animate);
    
    // Move train along the rails
    train.position.z += TRAIN_SPEED;
    
    // Reset position when train goes too far
    if (train.position.z > TRAIN_POSITION_RANGE / 2) {
        train.position.z = -TRAIN_POSITION_RANGE / 2;
    }
    
    // Slight camera sway for dynamic effect
    camera.position.x = Math.sin(Date.now() * 0.0005) * 0.3;
    
    renderer.render(scene, camera);
}

function stop3DHero() {
    isAnimating = false;
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
}

function start3DHero() {
    if (canvas && scene && !isAnimating) {
        isAnimating = true;
        animate();
    }
}

function toggle3DHero() {
    const canvas = document.getElementById('hero3d');
    const toggle = document.getElementById('toggle3d-status');
    
    if (!canvas || !toggle) return;
    
    const isCurrentlyEnabled = canvas.style.display !== 'none';
    
    if (isCurrentlyEnabled) {
        // Disable 3D
        canvas.style.display = 'none';
        toggle.textContent = 'Off';
        localStorage.setItem('railserve-3d-enabled', 'false');
        stop3DHero();
    } else {
        // Enable 3D
        canvas.style.display = 'block';
        toggle.textContent = 'On';
        localStorage.setItem('railserve-3d-enabled', 'true');
        
        // Initialize if not already done
        if (!scene) {
            init3DHero();
        } else {
            start3DHero();
        }
    }
}

// Handle window resize
function onWindowResize() {
    if (!camera || !renderer || !canvas) return;
    
    camera.aspect = canvas.offsetWidth / canvas.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
}

// Handle page visibility changes to pause/resume animation
function handleVisibilityChange() {
    if (document.hidden) {
        stop3DHero();
    } else {
        if (canvas && canvas.style.display !== 'none' && scene) {
            start3DHero();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set up the toggle button
    const toggle3DButton = document.getElementById('toggle3d');
    if (toggle3DButton) {
        toggle3DButton.addEventListener('click', toggle3DHero);
    }
    
    // Initialize 3D scene
    const initialized = init3DHero();
    
    // Update toggle status
    const toggle3DStatus = document.getElementById('toggle3d-status');
    if (toggle3DStatus) {
        const stored3DPreference = localStorage.getItem('railserve-3d-enabled');
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (stored3DPreference === 'false' || (prefersReducedMotion && stored3DPreference === null)) {
            toggle3DStatus.textContent = 'Off';
        } else {
            toggle3DStatus.textContent = initialized ? 'On' : 'Off';
        }
    }
    
    // Set up event listeners
    window.addEventListener('resize', onWindowResize);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Respect reduced motion preference changes
    const motionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    motionMediaQuery.addEventListener('change', function() {
        if (motionMediaQuery.matches) {
            // User enabled reduced motion, turn off 3D
            const canvas = document.getElementById('hero3d');
            const toggle = document.getElementById('toggle3d-status');
            if (canvas && toggle) {
                canvas.style.display = 'none';
                toggle.textContent = 'Off';
                localStorage.setItem('railserve-3d-enabled', 'false');
                stop3DHero();
            }
        }
    });
});