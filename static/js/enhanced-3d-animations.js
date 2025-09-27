/**
 * Enhanced 3D Animation System for RailServe 2025
 * =================================================
 * 
 * Features:
 * - Advanced train animations with realistic physics
 * - Dynamic particle systems for ambient effects
 * - Responsive performance optimization
 * - WebGL context recovery and error handling
 * - Mobile-optimized rendering
 * - Accessibility compliance
 */

class Enhanced3DAnimations {
    constructor() {
        this.scenes = new Map();
        this.animationFrameId = null;
        this.isInitialized = false;
        this.isAnimating = false;
        this.performanceMode = this.detectPerformanceMode();
        
        // Enhanced animation settings
        this.settings = {
            high: { 
                fps: 60, 
                particles: 100, 
                quality: 'high',
                shadows: true,
                antialiasing: true,
                postProcessing: true
            },
            medium: { 
                fps: 45, 
                particles: 60, 
                quality: 'medium',
                shadows: true,
                antialiasing: true,
                postProcessing: false
            },
            low: { 
                fps: 30, 
                particles: 30, 
                quality: 'low',
                shadows: false,
                antialiasing: false,
                postProcessing: false
            }
        };
        
        this.currentSettings = this.settings[this.performanceMode];
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / this.currentSettings.fps;
        
        // Animation state
        this.clock = new THREE.Clock();
        this.mixers = [];
        
        // Bind methods
        this.animate = this.animate.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.handleResize = this.handleResize.bind(this);
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    detectPerformanceMode() {
        // Advanced performance detection
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const hasLowMemory = navigator.deviceMemory && navigator.deviceMemory < 4;
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const isSlowConnection = navigator.connection && navigator.connection.effectiveType && 
                               ['slow-2g', '2g', '3g'].includes(navigator.connection.effectiveType);
        
        if (prefersReducedMotion) return 'low';
        if (isMobile || hasLowMemory || isSlowConnection) return 'medium';
        
        // Advanced WebGL capability detection
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        
        if (!gl) return 'low';
        
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        if (debugInfo) {
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
            
            // Check for high-performance GPUs
            if (renderer.toLowerCase().includes('nvidia') || renderer.toLowerCase().includes('radeon')) {
                return 'high';
            }
            
            // Check for integrated graphics that might struggle
            if (renderer.toLowerCase().includes('intel') && !renderer.toLowerCase().includes('iris')) {
                return 'medium';
            }
        }
        
        // Fallback based on other factors
        const pixelRatio = window.devicePixelRatio || 1;
        const screenSize = window.screen.width * window.screen.height * pixelRatio;
        
        return screenSize > 2073600 ? 'high' : 'medium'; // 1920x1080 baseline
    }
    
    setupEventListeners() {
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        window.addEventListener('resize', this.handleResize);
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
        
        // Handle WebGL context loss and restoration
        document.addEventListener('webglcontextlost', (e) => {
            e.preventDefault();
            this.handleContextLoss();
        });
        
        document.addEventListener('webglcontextrestored', () => {
            this.handleContextRestore();
        });
        
        // Performance monitoring
        if ('performance' in window) {
            setInterval(() => this.monitorPerformance(), 5000);
        }
    }
    
    async init() {
        if (this.isInitialized) return;
        
        try {
            // Check WebGL support
            if (!this.isWebGLSupported()) {
                console.warn('WebGL not supported, falling back to CSS animations');
                this.fallbackToCSS();
                return false;
            }
            
            // Initialize all scenes
            await this.initializeScenes();
            
            this.isInitialized = true;
            this.startAnimation();
            
            console.log(`Enhanced 3D animations initialized in ${this.performanceMode} performance mode`);
            return true;
            
        } catch (error) {
            console.error('Enhanced 3D animation initialization failed:', error);
            this.fallbackToCSS();
            return false;
        }
    }
    
    async initializeScenes() {
        // Initialize hero scene with advanced train animation
        const heroCanvas = document.getElementById('hero-3d-canvas');
        if (heroCanvas) {
            await this.initAdvancedTrainScene(heroCanvas);
        }
        
        // Initialize background particle system
        const bgCanvas = document.getElementById('bg-3d-canvas');
        if (bgCanvas) {
            await this.initAdvancedBackgroundScene(bgCanvas);
        }
    }
    
    async initAdvancedTrainScene(canvas) {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            alpha: true, 
            antialias: this.currentSettings.antialiasing,
            powerPreference: 'high-performance',
            stencil: false,
            depth: true
        });
        
        renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, this.currentSettings.quality === 'high' ? 2 : 1));
        
        // Advanced rendering settings
        if (this.currentSettings.shadows) {
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        }
        
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        renderer.outputEncoding = THREE.sRGBEncoding;
        
        // Enhanced scene setup
        scene.fog = new THREE.Fog(0x87CEEB, 50, 200);
        
        // Advanced lighting system
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        scene.add(ambientLight);
        
        const hemisphereLight = new THREE.HemisphereLight(0x87CEEB, 0x654321, 0.6);
        scene.add(hemisphereLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(20, 20, 10);
        directionalLight.castShadow = this.currentSettings.shadows;
        if (this.currentSettings.shadows) {
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            directionalLight.shadow.camera.near = 0.5;
            directionalLight.shadow.camera.far = 500;
            directionalLight.shadow.camera.left = -50;
            directionalLight.shadow.camera.right = 50;
            directionalLight.shadow.camera.top = 50;
            directionalLight.shadow.camera.bottom = -50;
        }
        scene.add(directionalLight);
        
        // Create enhanced train and environment
        const trainGroup = await this.createModernHighSpeedTrain();
        const railsGroup = await this.createRealisticRailway();
        const environmentGroup = await this.createEnvironment();
        
        scene.add(trainGroup);
        scene.add(railsGroup);
        scene.add(environmentGroup);
        
        // Advanced camera setup
        camera.position.set(0, 8, 15);
        camera.lookAt(0, 0, 0);
        
        // Store scene data
        this.scenes.set('hero', {
            scene,
            camera,
            renderer,
            canvas,
            train: trainGroup,
            rails: railsGroup,
            environment: environmentGroup,
            lights: { directional: directionalLight, hemisphere: hemisphereLight },
            animationData: {
                trainSpeed: 0.03,
                railLength: 40,
                cameraSwayAmount: 0.5,
                cameraSwaySpeed: 0.0003,
                trainRotation: 0,
                environmentRotation: 0,
                lightIntensity: 0.8
            }
        });
    }
    
    async initAdvancedBackgroundScene(canvas) {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ 
            canvas: canvas, 
            alpha: true, 
            antialias: false, // Background doesn't need antialiasing
            powerPreference: 'default'
        });
        
        renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
        renderer.setPixelRatio(1); // Lower pixel ratio for background
        
        // Create advanced particle system
        const particleSystem = await this.createAdvancedParticleSystem();
        const floatingShapes = await this.createFloatingGeometry();
        
        scene.add(particleSystem);
        floatingShapes.forEach(shape => scene.add(shape));
        
        camera.position.z = 15;
        
        // Store scene data
        this.scenes.set('background', {
            scene,
            camera,
            renderer,
            canvas,
            particles: particleSystem,
            shapes: floatingShapes,
            animationData: {
                cameraRadius: 3,
                cameraSpeed: 0.0002,
                particleSpeed: 0.005,
                shapeAnimationSpeed: 0.01,
                time: 0
            }
        });
    }
    
    async createModernHighSpeedTrain() {
        const trainGroup = new THREE.Group();
        
        // High-speed train body with modern aerodynamic design
        const bodyGeometry = new THREE.CapsuleGeometry(0.8, 4.0, 4, 8);
        const bodyMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x2563eb,
            shininess: 100,
            transparent: true,
            opacity: 0.95,
            emissive: 0x001122,
            emissiveIntensity: 0.1
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.set(0, 1.0, 0);
        body.rotation.z = Math.PI / 2;
        body.castShadow = this.currentSettings.shadows;
        body.receiveShadow = this.currentSettings.shadows;
        trainGroup.add(body);
        
        // Aerodynamic nose cone
        const noseGeometry = new THREE.ConeGeometry(0.6, 1.5, 8);
        const noseMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x1d4ed8,
            shininess: 120,
            emissive: 0x000066
        });
        const nose = new THREE.Mesh(noseGeometry, noseMaterial);
        nose.position.set(0, 1.0, 2.75);
        nose.rotation.x = Math.PI / 2;
        nose.castShadow = this.currentSettings.shadows;
        trainGroup.add(nose);
        
        // Modern pantograph (power collector)
        const pantographGeometry = new THREE.BoxGeometry(0.1, 1.0, 0.1);
        const pantographMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 });
        const pantograph = new THREE.Mesh(pantographGeometry, pantographMaterial);
        pantograph.position.set(0, 2.0, 0);
        trainGroup.add(pantograph);
        
        // Advanced wheel system
        const wheelGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 16);
        const wheelMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x222222,
            shininess: 80,
            metalness: 0.7
        });
        
        const wheelPositions = [
            [-0.7, 0.3, -1.5], [0.7, 0.3, -1.5],
            [-0.7, 0.3, 0], [0.7, 0.3, 0],
            [-0.7, 0.3, 1.5], [0.7, 0.3, 1.5]
        ];
        
        wheelPositions.forEach((pos, index) => {
            const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
            wheel.position.set(pos[0], pos[1], pos[2]);
            wheel.rotation.z = Math.PI / 2;
            wheel.castShadow = this.currentSettings.shadows;
            wheel.userData = { isWheel: true, originalRotation: wheel.rotation.x };
            trainGroup.add(wheel);
        });
        
        // LED strip lighting
        const stripGeometry = new THREE.BoxGeometry(0.05, 0.05, 4.0);
        const stripMaterial = new THREE.MeshBasicMaterial({ 
            color: 0x00ffff,
            emissive: 0x003366,
            transparent: true,
            opacity: 0.8
        });
        const leftStrip = new THREE.Mesh(stripGeometry, stripMaterial);
        leftStrip.position.set(-0.85, 1.0, 0);
        trainGroup.add(leftStrip);
        
        const rightStrip = new THREE.Mesh(stripGeometry, stripMaterial);
        rightStrip.position.set(0.85, 1.0, 0);
        trainGroup.add(rightStrip);
        
        // Dynamic windows with interior lighting
        const windowGeometry = new THREE.PlaneGeometry(0.4, 0.6);
        const windowMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x87ceeb,
            transparent: true,
            opacity: 0.3,
            emissive: 0x002244,
            emissiveIntensity: 0.2
        });
        
        for (let i = -1.5; i <= 1.5; i += 0.75) {
            const leftWindow = new THREE.Mesh(windowGeometry, windowMaterial);
            leftWindow.position.set(-0.81, 1.2, i);
            leftWindow.rotation.y = Math.PI / 2;
            trainGroup.add(leftWindow);
            
            const rightWindow = new THREE.Mesh(windowGeometry, windowMaterial);
            rightWindow.position.set(0.81, 1.2, i);
            rightWindow.rotation.y = -Math.PI / 2;
            trainGroup.add(rightWindow);
        }
        
        trainGroup.position.z = -20;
        return trainGroup;
    }
    
    async createRealisticRailway() {
        const railGroup = new THREE.Group();
        
        // Modern concrete sleepers
        const sleeperGeometry = new THREE.BoxGeometry(2.8, 0.15, 0.3);
        const sleeperMaterial = new THREE.MeshLambertMaterial({ color: 0x888888 });
        
        // Steel rails with realistic wear
        const railGeometry = new THREE.BoxGeometry(0.15, 0.2, 60);
        const railMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x666666,
            shininess: 100,
            metalness: 0.8
        });
        
        // Left and right rails
        const leftRail = new THREE.Mesh(railGeometry, railMaterial);
        leftRail.position.set(-0.75, 0.1, 0);
        leftRail.castShadow = this.currentSettings.shadows;
        railGroup.add(leftRail);
        
        const rightRail = new THREE.Mesh(railGeometry, railMaterial);
        rightRail.position.set(0.75, 0.1, 0);
        rightRail.castShadow = this.currentSettings.shadows;
        railGroup.add(rightRail);
        
        // Railway sleepers with realistic spacing
        for (let i = -30; i <= 30; i += 0.6) {
            const sleeper = new THREE.Mesh(sleeperGeometry, sleeperMaterial);
            sleeper.position.set(0, 0, i);
            sleeper.receiveShadow = this.currentSettings.shadows;
            railGroup.add(sleeper);
        }
        
        // Ballast stones (for high quality only)
        if (this.currentSettings.quality === 'high') {
            const ballastGeometry = new THREE.SphereGeometry(0.03, 6, 4);
            const ballastMaterial = new THREE.MeshLambertMaterial({ color: 0x777777 });
            
            for (let i = 0; i < 200; i++) {
                const ballast = new THREE.Mesh(ballastGeometry, ballastMaterial);
                ballast.position.set(
                    (Math.random() - 0.5) * 4,
                    -0.1,
                    (Math.random() - 0.5) * 60
                );
                ballast.scale.set(
                    0.5 + Math.random() * 0.5,
                    0.5 + Math.random() * 0.5,
                    0.5 + Math.random() * 0.5
                );
                railGroup.add(ballast);
            }
        }
        
        return railGroup;
    }
    
    async createEnvironment() {
        const envGroup = new THREE.Group();
        
        // Ground plane
        const groundGeometry = new THREE.PlaneGeometry(100, 100);
        const groundMaterial = new THREE.MeshLambertMaterial({ 
            color: 0x3a5f3a,
            transparent: true,
            opacity: 0.8
        });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.2;
        ground.receiveShadow = this.currentSettings.shadows;
        envGroup.add(ground);
        
        // Trees along the railway
        if (this.currentSettings.quality !== 'low') {
            for (let i = 0; i < 20; i++) {
                const tree = this.createTree();
                tree.position.set(
                    (Math.random() > 0.5 ? 1 : -1) * (5 + Math.random() * 10),
                    0,
                    (Math.random() - 0.5) * 40
                );
                tree.scale.set(0.5 + Math.random() * 0.5, 0.5 + Math.random() * 0.5, 0.5 + Math.random() * 0.5);
                envGroup.add(tree);
            }
        }
        
        return envGroup;
    }
    
    createTree() {
        const treeGroup = new THREE.Group();
        
        // Trunk
        const trunkGeometry = new THREE.CylinderGeometry(0.1, 0.15, 2);
        const trunkMaterial = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
        const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
        trunk.position.y = 1;
        trunk.castShadow = this.currentSettings.shadows;
        treeGroup.add(trunk);
        
        // Foliage
        const foliageGeometry = new THREE.SphereGeometry(1, 8, 6);
        const foliageMaterial = new THREE.MeshLambertMaterial({ color: 0x228B22 });
        const foliage = new THREE.Mesh(foliageGeometry, foliageMaterial);
        foliage.position.y = 2.5;
        foliage.castShadow = this.currentSettings.shadows;
        treeGroup.add(foliage);
        
        return treeGroup;
    }
    
    async createAdvancedParticleSystem() {
        const particleCount = this.currentSettings.particles;
        const positions = new Float32Array(particleCount * 3);
        const velocities = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            // Position
            positions[i * 3] = (Math.random() - 0.5) * 50;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 50;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 50;
            
            // Velocity
            velocities[i * 3] = (Math.random() - 0.5) * 0.02;
            velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
            velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;
            
            // Colors (blue to cyan gradient)
            colors[i * 3] = 0.2 + Math.random() * 0.3;     // R
            colors[i * 3 + 1] = 0.5 + Math.random() * 0.5; // G
            colors[i * 3 + 2] = 0.8 + Math.random() * 0.2; // B
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({
            size: 0.1,
            transparent: true,
            opacity: 0.6,
            vertexColors: true,
            blending: THREE.AdditiveBlending
        });
        
        const particles = new THREE.Points(geometry, material);
        particles.userData = { isParticleSystem: true };
        
        return particles;
    }
    
    async createFloatingGeometry() {
        const shapes = [];
        const numShapes = Math.floor(this.currentSettings.particles / 5);
        
        // Modern geometric shapes
        const geometries = [
            new THREE.OctahedronGeometry(0.5),
            new THREE.TetrahedronGeometry(0.6),
            new THREE.IcosahedronGeometry(0.4),
            new THREE.DodecahedronGeometry(0.5),
            new THREE.TorusGeometry(0.3, 0.1, 8, 16),
            new THREE.TorusKnotGeometry(0.3, 0.1, 64, 8)
        ];
        
        // Modern color palette
        const colors = [0x3b82f6, 0x8b5cf6, 0x10b981, 0xf59e0b, 0xef4444, 0x06b6d4, 0x8b5a2b];
        
        for (let i = 0; i < numShapes; i++) {
            const geometry = geometries[Math.floor(Math.random() * geometries.length)];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            const material = new THREE.MeshPhongMaterial({
                color: color,
                transparent: true,
                opacity: 0.4,
                emissive: color,
                emissiveIntensity: 0.05,
                shininess: 100
            });
            
            const mesh = new THREE.Mesh(geometry, material);
            
            // Random positioning
            mesh.position.x = (Math.random() - 0.5) * 40;
            mesh.position.y = (Math.random() - 0.5) * 40;
            mesh.position.z = (Math.random() - 0.5) * 40;
            
            // Random rotation
            mesh.rotation.x = Math.random() * Math.PI;
            mesh.rotation.y = Math.random() * Math.PI;
            mesh.rotation.z = Math.random() * Math.PI;
            
            // Random scale
            const scale = 0.2 + Math.random() * 0.8;
            mesh.scale.set(scale, scale, scale);
            
            // Animation data
            mesh.userData = {
                rotationSpeed: {
                    x: (Math.random() - 0.5) * 0.02,
                    y: (Math.random() - 0.5) * 0.02,
                    z: (Math.random() - 0.5) * 0.02
                },
                floatSpeed: Math.random() * 0.01 + 0.005,
                floatOffset: Math.random() * Math.PI * 2,
                initialPosition: mesh.position.clone(),
                pulsePeriod: 2 + Math.random() * 3
            };
            
            shapes.push(mesh);
        }
        
        return shapes;
    }
    
    startAnimation() {
        if (this.isAnimating) return;
        this.isAnimating = true;
        this.clock.start();
        this.animate();
    }
    
    stopAnimation() {
        this.isAnimating = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
        this.clock.stop();
    }
    
    animate(currentTime = 0) {
        if (!this.isAnimating) return;
        
        // Frame rate throttling
        if (currentTime - this.lastFrameTime < this.frameInterval) {
            this.animationFrameId = requestAnimationFrame(this.animate);
            return;
        }
        
        this.lastFrameTime = currentTime;
        const deltaTime = this.clock.getDelta();
        const elapsedTime = this.clock.getElapsedTime();
        
        try {
            // Update animation mixers
            this.mixers.forEach(mixer => mixer.update(deltaTime));
            
            // Animate all scenes
            this.scenes.forEach((sceneData, key) => {
                this.animateScene(key, sceneData, elapsedTime, deltaTime);
            });
        } catch (error) {
            console.error('Animation error:', error);
            this.handleAnimationError(error);
        }
        
        this.animationFrameId = requestAnimationFrame(this.animate);
    }
    
    animateScene(key, sceneData, elapsedTime, deltaTime) {
        const { scene, camera, renderer, canvas } = sceneData;
        
        // Check if canvas is visible
        if (!this.isCanvasVisible(canvas)) return;
        
        if (key === 'hero') {
            this.animateHeroScene(sceneData, elapsedTime, deltaTime);
        } else if (key === 'background') {
            this.animateBackgroundScene(sceneData, elapsedTime, deltaTime);
        }
        
        // Render the scene
        renderer.render(scene, camera);
    }
    
    animateHeroScene(sceneData, elapsedTime, deltaTime) {
        const { train, camera, lights, animationData } = sceneData;
        
        // Advanced train movement with realistic physics
        train.position.z += animationData.trainSpeed;
        if (train.position.z > 25) {
            train.position.z = -25;
        }
        
        // Animate train wheels with proper rotation
        train.children.forEach(child => {
            if (child.userData.isWheel) {
                child.rotation.x += animationData.trainSpeed * 3;
            }
        });
        
        // Advanced camera movement with multiple motion types
        const time = elapsedTime * animationData.cameraSwaySpeed;
        camera.position.x = Math.sin(time) * animationData.cameraSwayAmount;
        camera.position.y = 8 + Math.cos(time * 0.7) * 0.3;
        camera.position.z = 15 + Math.sin(time * 0.3) * 2;
        
        // Dynamic lighting effects
        const lightIntensity = animationData.lightIntensity + Math.sin(elapsedTime * 0.5) * 0.2;
        lights.directional.intensity = lightIntensity;
        
        // Environmental effects
        if (sceneData.environment) {
            sceneData.environment.rotation.y = elapsedTime * 0.02;
        }
        
        // LED strip pulsing effect
        train.children.forEach(child => {
            if (child.material && child.material.emissive) {
                const pulse = Math.sin(elapsedTime * 4) * 0.5 + 0.5;
                child.material.emissiveIntensity = 0.1 + pulse * 0.2;
            }
        });
    }
    
    animateBackgroundScene(sceneData, elapsedTime, deltaTime) {
        const { particles, shapes, camera, animationData } = sceneData;
        
        animationData.time = elapsedTime;
        
        // Animate particle system
        if (particles && particles.userData.isParticleSystem) {
            const positions = particles.geometry.attributes.position.array;
            const velocities = particles.geometry.attributes.velocity.array;
            
            for (let i = 0; i < positions.length; i += 3) {
                // Update positions based on velocities
                positions[i] += velocities[i];
                positions[i + 1] += velocities[i + 1];
                positions[i + 2] += velocities[i + 2];
                
                // Boundary wrapping
                if (Math.abs(positions[i]) > 25) velocities[i] *= -1;
                if (Math.abs(positions[i + 1]) > 25) velocities[i + 1] *= -1;
                if (Math.abs(positions[i + 2]) > 25) velocities[i + 2] *= -1;
            }
            
            particles.geometry.attributes.position.needsUpdate = true;
        }
        
        // Animate floating shapes with advanced motion
        shapes.forEach((shape, index) => {
            // Complex rotation
            shape.rotation.x += shape.userData.rotationSpeed.x;
            shape.rotation.y += shape.userData.rotationSpeed.y;
            shape.rotation.z += shape.userData.rotationSpeed.z;
            
            // Advanced floating motion with multiple sine waves
            const time = elapsedTime * shape.userData.floatSpeed;
            const offset = shape.userData.floatOffset;
            
            shape.position.y = shape.userData.initialPosition.y + 
                               Math.sin(time + offset) * 3 + 
                               Math.sin(time * 2 + offset) * 1;
            shape.position.x = shape.userData.initialPosition.x + 
                               Math.cos(time + offset) * 2;
            shape.position.z = shape.userData.initialPosition.z + 
                               Math.sin(time * 0.5 + offset) * 1;
            
            // Pulsing scale effect
            const pulseTime = elapsedTime / shape.userData.pulsePeriod;
            const pulseScale = 1 + Math.sin(pulseTime * Math.PI * 2) * 0.1;
            shape.scale.setScalar(shape.scale.x * pulseScale / (shape.userData.lastPulseScale || 1));
            shape.userData.lastPulseScale = pulseScale;
            
            // Dynamic opacity based on distance from camera
            const distance = shape.position.distanceTo(camera.position);
            shape.material.opacity = Math.max(0.1, Math.min(0.6, 30 / distance));
        });
        
        // Smooth camera orbit with multiple motion layers
        const time = elapsedTime * animationData.cameraSpeed;
        camera.position.x = Math.sin(time) * animationData.cameraRadius + Math.cos(time * 2) * 0.5;
        camera.position.y = Math.cos(time * 0.7) * animationData.cameraRadius * 0.5 + Math.sin(time * 3) * 0.3;
        camera.position.z = 15 + Math.sin(time * 0.3) * 2;
        camera.lookAt(0, 0, 0);
        
        // Theme-based adjustments
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        shapes.forEach(shape => {
            shape.material.opacity *= isDark ? 0.7 : 1.0;
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
        console.error('Enhanced 3D animation error:', error);
        if (error.name === 'WebGLRenderingContext') {
            this.fallbackToCSS();
        }
    }
    
    monitorPerformance() {
        if (this.isAnimating && 'performance' in window) {
            const frameRate = 1000 / this.frameInterval;
            const actualFrameRate = 1000 / (performance.now() - this.lastFrameTime);
            
            if (actualFrameRate < frameRate * 0.7 && this.performanceMode !== 'low') {
                console.warn('Performance degradation detected, considering mode adjustment');
                // Could implement automatic quality reduction here
            }
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
            const gl = canvas.getContext('webgl2') || 
                      canvas.getContext('webgl') || 
                      canvas.getContext('experimental-webgl');
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
        this.mixers = [];
        
        // Remove event listeners
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        window.removeEventListener('resize', this.handleResize);
    }
    
    // Public API methods
    toggle() {
        if (this.isAnimating) {
            this.stopAnimation();
            localStorage.setItem('railserve-3d-enabled', 'false');
            return false;
        } else {
            if (!this.isInitialized) {
                this.init();
            } else {
                this.startAnimation();
            }
            localStorage.setItem('railserve-3d-enabled', 'true');
            return true;
        }
    }
    
    setQuality(quality) {
        if (['low', 'medium', 'high'].includes(quality)) {
            this.performanceMode = quality;
            this.currentSettings = this.settings[quality];
            this.frameInterval = 1000 / this.currentSettings.fps;
            
            // Reinitialize if needed
            if (this.isInitialized) {
                this.cleanup();
                this.isInitialized = false;
                this.init();
            }
        }
    }
}

// Global instance
window.enhanced3D = new Enhanced3DAnimations();

// Global toggle function for UI
window.toggle3DHero = function() {
    const isEnabled = window.enhanced3D.toggle();
    const statusElement = document.getElementById('3d-status');
    if (statusElement) {
        statusElement.textContent = isEnabled ? 'On' : 'Off';
    }
    return isEnabled;
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check user preferences
    const stored3DPreference = localStorage.getItem('railserve-3d-enabled');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Initialize if enabled or not explicitly disabled
    if (stored3DPreference !== 'false' && !prefersReducedMotion) {
        window.enhanced3D.init();
    }
    
    // Update UI status
    const statusElement = document.getElementById('3d-status');
    if (statusElement) {
        statusElement.textContent = window.enhanced3D.isAnimating ? 'On' : 'Off';
    }
});

// CSS fallback animations for no-webgl class
const cssAnimationStyles = `
.no-webgl .hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-size: 400% 400%;
    animation: gradient-shift 8s ease-in-out infinite;
}

.no-webgl .feature-card {
    animation: float 4s ease-in-out infinite;
}

.no-webgl .feature-card:nth-child(2) { animation-delay: 1s; }
.no-webgl .feature-card:nth-child(3) { animation-delay: 2s; }
.no-webgl .feature-card:nth-child(4) { animation-delay: 3s; }

.no-webgl .train-card {
    animation: subtle-float 6s ease-in-out infinite;
}

.no-webgl .train-card:nth-child(even) { animation-delay: 3s; }

@keyframes gradient-shift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

@keyframes subtle-float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    33% { transform: translateY(-5px) rotate(0.5deg); }
    66% { transform: translateY(-2px) rotate(-0.5deg); }
}
`;

// Inject CSS fallback styles
const style = document.createElement('style');
style.textContent = cssAnimationStyles;
document.head.appendChild(style);