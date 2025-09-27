/**
 * Modern 3D Animation System - 2025
 * ================================
 * 
 * Unified 3D animation framework with:
 * - WebGL context recovery and error handling
 * - Performance optimization with intersection observers
 * - Smooth train animations and floating geometric elements
 * - Mobile-responsive design and accessibility
 * - Memory leak prevention and cleanup
 */

class Modern3DAnimations {
    constructor() {
        this.scenes = new Map();
        this.animationFrameId = null;
        this.isInitialized = false;
        this.isAnimating = false;
        this.performanceMode = this.detectPerformanceMode();
        
        // Animation settings based on performance mode
        this.settings = {
            high: { fps: 60, particles: 20, quality: 'high' },
            medium: { fps: 30, particles: 12, quality: 'medium' },
            low: { fps: 15, particles: 6, quality: 'low' }
        };
        
        this.currentSettings = this.settings[this.performanceMode];
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / this.currentSettings.fps;
        
        // Bind methods
        this.animate = this.animate.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.handleResize = this.handleResize.bind(this);
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    detectPerformanceMode() {
        // Check device capabilities
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const hasLowMemory = navigator.deviceMemory && navigator.deviceMemory < 4;
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (prefersReducedMotion) return 'low';
        if (isMobile || hasLowMemory) return 'medium';
        
        // Check WebGL support and performance
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) return 'low';
        
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            if (renderer.toLowerCase().includes('intel') && !renderer.toLowerCase().includes('iris')) {
                return 'medium';
            }
        }
        
        return 'high';
    }
    
    setupEventListeners() {
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        window.addEventListener('resize', this.handleResize);
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
        
        // Handle WebGL context loss
        document.addEventListener('webglcontextlost', (e) => {
            e.preventDefault();
            this.handleContextLoss();
        });
        
        document.addEventListener('webglcontextrestored', () => {
            this.handleContextRestore();
        });
    }
    
    async init() {
        if (this.isInitialized) return;
        
        try {
            // Check WebGL support
            if (!this.isWebGLSupported()) {
                console.warn('WebGL not supported, skipping 3D animations');
                return;
            }
            
            // Initialize scenes
            await this.initializeScenes();
            
            this.isInitialized = true;
            this.startAnimation();
            
            console.log(`3D animations initialized in ${this.performanceMode} performance mode`);
            
        } catch (error) {
            console.error('3D animation initialization failed:', error);
            this.fallbackToCSS();
        }
    }
    
    async initializeScenes() {
        // Initialize hero train scene
        const heroCanvas = document.getElementById('hero-3d-canvas');
        if (heroCanvas) {
            await this.initTrainScene(heroCanvas);
        }
        
        // Initialize floating background scene
        const bgCanvas = document.getElementById('bg-3d-canvas');
        if (bgCanvas) {
            await this.initBackgroundScene(bgCanvas);
        }
    }
    
    async initTrainScene(canvas) {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            alpha: true, 
            antialias: this.currentSettings.quality !== 'low',
            powerPreference: 'high-performance'
        });
        
        renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, this.currentSettings.quality === 'high' ? 2 : 1));
        renderer.shadowMap.enabled = this.currentSettings.quality === 'high';
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Scene setup
        scene.fog = new THREE.Fog(0x87CEEB, 20, 100);
        
        // Enhanced lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = this.currentSettings.quality === 'high';
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        scene.add(directionalLight);
        
        // Create enhanced train and rails
        const trainGroup = await this.createModernTrain();
        const railsGroup = await this.createModernRails();
        
        scene.add(trainGroup);
        scene.add(railsGroup);
        
        // Camera setup
        camera.position.set(0, 4, 8);
        camera.lookAt(0, 0, 0);
        
        // Store scene data
        this.scenes.set('train', {
            scene,
            camera,
            renderer,
            canvas,
            train: trainGroup,
            rails: railsGroup,
            animationData: {
                trainSpeed: 0.02,
                railLength: 20,
                cameraSwayAmount: 0.3,
                cameraSwaySpeed: 0.0005
            }
        });
    }
    
    async initBackgroundScene(canvas) {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            alpha: true, 
            antialias: false // Background doesn't need antialiasing
        });
        
        renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        renderer.setPixelRatio(1); // Lower pixel ratio for background
        
        // Create floating geometries
        const shapes = await this.createFloatingShapes();
        shapes.forEach(shape => scene.add(shape));
        
        camera.position.z = 10;
        
        // Store scene data
        this.scenes.set('background', {
            scene,
            camera,
            renderer,
            canvas,
            shapes,
            animationData: {
                cameraRadius: 2,
                cameraSpeed: 0.0005,
                shapeAnimationSpeed: 0.01
            }
        });
    }
    
    async createModernTrain() {
        const trainGroup = new THREE.Group();
        
        // Enhanced train body with realistic proportions
        const bodyGeometry = new THREE.BoxGeometry(1.5, 1.0, 3.0);
        const bodyMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x1E90FF,
            shininess: 100,
            transparent: true,
            opacity: 0.9
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.set(0, 0.5, 0);
        body.castShadow = true;
        body.receiveShadow = true;
        trainGroup.add(body);
        
        // Sleek roof
        const roofGeometry = new THREE.BoxGeometry(1.6, 0.1, 3.1);
        const roofMaterial = new THREE.MeshPhongMaterial({ color: 0x4169E1 });
        const roof = new THREE.Mesh(roofGeometry, roofMaterial);
        roof.position.set(0, 1.05, 0);
        trainGroup.add(roof);
        
        // Modern locomotive front
        const frontGeometry = new THREE.ConeGeometry(0.4, 0.8, 8);
        const frontMaterial = new THREE.MeshPhongMaterial({ 
            color: 0xFF4500,
            emissive: 0x441100
        });
        const front = new THREE.Mesh(frontGeometry, frontMaterial);
        front.position.set(0, 0.5, 1.9);
        front.rotation.x = Math.PI / 2;
        trainGroup.add(front);
        
        // Enhanced wheels with rotation animation
        const wheelGeometry = new THREE.CylinderGeometry(0.25, 0.25, 0.15, 16);
        const wheelMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x333333,
            shininess: 50
        });
        
        const wheelPositions = [
            [-0.6, 0.0, -1.0], [0.6, 0.0, -1.0],
            [-0.6, 0.0, 1.0], [0.6, 0.0, 1.0]
        ];
        
        wheelPositions.forEach(pos => {
            const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
            wheel.position.set(pos[0], pos[1], pos[2]);
            wheel.rotation.z = Math.PI / 2;
            wheel.castShadow = true;
            trainGroup.add(wheel);
        });
        
        // Windows
        const windowGeometry = new THREE.PlaneGeometry(0.3, 0.4);
        const windowMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x87CEEB,
            transparent: true,
            opacity: 0.7,
            emissive: 0x001122
        });
        
        // Side windows
        for (let i = -1; i <= 1; i++) {
            const leftWindow = new THREE.Mesh(windowGeometry, windowMaterial);
            leftWindow.position.set(-0.76, 0.7, i);
            leftWindow.rotation.y = Math.PI / 2;
            trainGroup.add(leftWindow);
            
            const rightWindow = new THREE.Mesh(windowGeometry, windowMaterial);
            rightWindow.position.set(0.76, 0.7, i);
            rightWindow.rotation.y = -Math.PI / 2;
            trainGroup.add(rightWindow);
        }
        
        trainGroup.position.z = -10;
        return trainGroup;
    }
    
    async createModernRails() {
        const railGroup = new THREE.Group();
        
        // Enhanced rails with realistic materials
        const railGeometry = new THREE.BoxGeometry(0.1, 0.15, 25);
        const railMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x8B4513,
            shininess: 80
        });
        
        // Left and right rails
        const leftRail = new THREE.Mesh(railGeometry, railMaterial);
        leftRail.position.set(-0.75, -0.3, 0);
        leftRail.castShadow = true;
        railGroup.add(leftRail);
        
        const rightRail = new THREE.Mesh(railGeometry, railMaterial);
        rightRail.position.set(0.75, -0.3, 0);
        rightRail.castShadow = true;
        railGroup.add(rightRail);
        
        // Railway ties with varied spacing
        const tieGeometry = new THREE.BoxGeometry(2.2, 0.12, 0.25);
        const tieMaterial = new THREE.MeshLambertMaterial({ color: 0x654321 });
        
        for (let i = -12; i <= 12; i += 1.2) {
            const tie = new THREE.Mesh(tieGeometry, tieMaterial);
            tie.position.set(0, -0.37, i);
            tie.receiveShadow = true;
            railGroup.add(tie);
        }
        
        // Add gravel/ballast effect
        if (this.currentSettings.quality === 'high') {
            const gravelGeometry = new THREE.SphereGeometry(0.02, 6, 4);
            const gravelMaterial = new THREE.MeshLambertMaterial({ color: 0x888888 });
            
            for (let i = 0; i < 100; i++) {
                const gravel = new THREE.Mesh(gravelGeometry, gravelMaterial);
                gravel.position.set(
                    (Math.random() - 0.5) * 3,
                    -0.45,
                    (Math.random() - 0.5) * 20
                );
                railGroup.add(gravel);
            }
        }
        
        return railGroup;
    }
    
    async createFloatingShapes() {
        const shapes = [];
        const numShapes = this.currentSettings.particles;
        
        // Modern geometric shapes
        const geometries = [
            new THREE.OctahedronGeometry(0.5),
            new THREE.TetrahedronGeometry(0.6),
            new THREE.IcosahedronGeometry(0.4),
            new THREE.DodecahedronGeometry(0.5),
            new THREE.ConeGeometry(0.4, 0.8, 6),
            new THREE.CylinderGeometry(0.3, 0.3, 0.6, 8)
        ];
        
        // Enhanced materials with modern colors
        const colors = [0x3b82f6, 0x8b5cf6, 0x10b981, 0xf59e0b, 0xef4444, 0x06b6d4];
        
        for (let i = 0; i < numShapes; i++) {
            const geometry = geometries[Math.floor(Math.random() * geometries.length)];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            const material = new THREE.MeshPhongMaterial({
                color: color,
                transparent: true,
                opacity: 0.6,
                emissive: color,
                emissiveIntensity: 0.1,
                shininess: 100
            });
            
            const mesh = new THREE.Mesh(geometry, material);
            
            // Random positioning
            mesh.position.x = (Math.random() - 0.5) * 25;
            mesh.position.y = (Math.random() - 0.5) * 25;
            mesh.position.z = (Math.random() - 0.5) * 25;
            
            // Random rotation
            mesh.rotation.x = Math.random() * Math.PI;
            mesh.rotation.y = Math.random() * Math.PI;
            mesh.rotation.z = Math.random() * Math.PI;
            
            // Random scale
            const scale = 0.3 + Math.random() * 1.2;
            mesh.scale.set(scale, scale, scale);
            
            // Animation data
            mesh.userData = {
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.03,
                    y: (Math.random() - 0.5) * 0.03,
                    z: (Math.random() - 0.5) * 0.03
                },
                floatSpeed: Math.random() * 0.02 + 0.01,
                floatOffset: Math.random() * Math.PI * 2,
                initialPosition: mesh.position.clone()
            };
            
            shapes.push(mesh);
        }
        
        return shapes;
    }
    
    startAnimation() {
        if (this.isAnimating) return;
        this.isAnimating = true;
        this.animate();
    }
    
    stopAnimation() {
        this.isAnimating = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }
    
    animate(currentTime = 0) {
        if (!this.isAnimating) return;
        
        // Frame rate throttling
        if (currentTime - this.lastFrameTime < this.frameInterval) {
            this.animationFrameId = requestAnimationFrame(this.animate);
            return;
        }
        
        this.lastFrameTime = currentTime;
        
        try {
            // Animate all scenes
            this.scenes.forEach((sceneData, key) => {
                this.animateScene(key, sceneData, currentTime);
            });
        } catch (error) {
            console.error('Animation error:', error);
            this.handleAnimationError(error);
        }
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    }
    
    animateScene(key, sceneData, currentTime) {
        const { scene, camera, renderer, canvas } = sceneData;
        
        // Check if canvas is visible (intersection observer alternative)
        if (!this.isCanvasVisible(canvas)) return;
        
        if (key === 'train') {
            this.animateTrainScene(sceneData, currentTime);
        } else if (key === 'background') {
            this.animateBackgroundScene(sceneData, currentTime);
        }
        
        // Render the scene
        renderer.render(scene, camera);
    }
    
    animateTrainScene(sceneData, currentTime) {
        const { train, camera, animationData } = sceneData;
        
        // Move train
        train.position.z += animationData.trainSpeed;
        if (train.position.z > 10) {
            train.position.z = -10;
        }
        
        // Animate train wheels
        train.children.forEach(child => {
            if (child.geometry && child.geometry.type === 'CylinderGeometry') {
                child.rotation.x += animationData.trainSpeed * 2;
            }
        });
        
        // Smooth camera movement
        const time = currentTime * animationData.cameraSwaySpeed;
        camera.position.x = Math.sin(time) * animationData.cameraSwayAmount;
        camera.position.y = 4 + Math.cos(time * 0.7) * 0.2;
        
        // Dynamic lighting based on train position
        const lightIntensity = 0.8 + Math.sin(train.position.z * 0.1) * 0.2;
        sceneData.scene.children.forEach(child => {
            if (child.type === 'DirectionalLight') {
                child.intensity = lightIntensity;
            }
        });
    }
    
    animateBackgroundScene(sceneData, currentTime) {
        const { shapes, camera, animationData } = sceneData;
        
        // Animate floating shapes
        shapes.forEach((shape, index) => {
            // Rotation
            shape.rotation.x += shape.userData.rotationSpeed.x;
            shape.rotation.y += shape.userData.rotationSpeed.y;
            shape.rotation.z += shape.userData.rotationSpeed.z;
            
            // Floating motion
            const time = currentTime * shape.userData.floatSpeed * 0.001;
            shape.position.y = shape.userData.initialPosition.y + 
                               Math.sin(time + shape.userData.floatOffset) * 2;
            shape.position.x = shape.userData.initialPosition.x + 
                               Math.cos(time + shape.userData.floatOffset) * 1;
        });
        
        // Smooth camera orbit
        const time = currentTime * animationData.cameraSpeed;
        camera.position.x = Math.sin(time) * animationData.cameraRadius;
        camera.position.y = Math.cos(time * 0.7) * animationData.cameraRadius * 0.5;
        camera.lookAt(0, 0, 0);
        
        // Theme-based opacity adjustment
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        shapes.forEach(shape => {
            shape.material.opacity = isDark ? 0.4 : 0.25;
        });
    }
    
    isCanvasVisible(canvas) {
        const rect = canvas.getBoundingClientRect();
        return rect.bottom >= 0 && rect.right >= 0 && 
               rect.top <= window.innerHeight && rect.left <= window.innerWidth;
    }
    
    handleVisibilityChange() {
        if (document.hidden) {
            this.stopAnimation();
        } else if (this.isInitialized) {
            this.startAnimation();
        }
    }
    
    handleResize() {
        this.scenes.forEach((sceneData) => {
            const { camera, renderer, canvas } = sceneData;
            
            camera.aspect = canvas.offsetWidth / canvas.offsetHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        });
    }
    
    handleContextLoss() {
        console.warn('WebGL context lost, stopping animations');
        this.stopAnimation();
    }
    
    handleContextRestore() {
        console.log('WebGL context restored, reinitializing');
        this.isInitialized = false;
        this.init();
    }
    
    handleAnimationError(error) {
        console.error('3D animation error:', error);
        if (error.name === 'WebGLRenderingContext') {
            this.fallbackToCSS();
        }
    }
    
    fallbackToCSS() {
        console.log('Falling back to CSS animations');
        
        // Hide 3D canvases
        this.scenes.forEach(({ canvas }) => {
            if (canvas) canvas.style.display = 'none';
        });
        
        // Enable CSS fallback animations
        document.documentElement.classList.add('no-webgl');
        
        this.cleanup();
    }
    
    isWebGLSupported() {
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            return !!gl && !!gl.getParameter && !!gl.getParameter(gl.VERSION);
        } catch (e) {
            return false;
        }
    }
    
    cleanup() {
        this.stopAnimation();
        
        this.scenes.forEach((sceneData) => {
            const { scene, renderer } = sceneData;
            
            // Dispose of geometries and materials
            scene.traverse((child) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(material => material.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            });
            
            // Dispose of renderer
            renderer.dispose();
        });
        
        this.scenes.clear();
        
        // Remove event listeners
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        window.removeEventListener('resize', this.handleResize);
    }
}

// Global instance
window.modern3D = new Modern3DAnimations();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.modern3D.init();
});

// CSS fallback animations
const cssAnimationStyles = `
.no-webgl .hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    animation: gradient-shift 6s ease-in-out infinite;
}

.no-webgl .feature-card {
    animation: float 3s ease-in-out infinite;
}

.no-webgl .feature-card:nth-child(2) { animation-delay: 0.5s; }
.no-webgl .feature-card:nth-child(3) { animation-delay: 1s; }
.no-webgl .feature-card:nth-child(4) { animation-delay: 1.5s; }

@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
`;

// Inject CSS fallback styles
const style = document.createElement('style');
style.textContent = cssAnimationStyles;
document.head.appendChild(style);