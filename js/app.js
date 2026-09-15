/**
 * Main Application - Orchestrates particle system, gesture detection, and UI
 */
class App {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particleSystem = null;
        this.gestureDetector = null;
        this.uiController = null;
        this.lastTime = performance.now();
        this.deltaTime = 0;
        this.isHandOpen = false;
        
        this.init();
    }

    init() {
        this.setupThreeJS();
        this.setupParticleSystem();
        this.setupGestureDetection();
        this.setupUI();
        this.setupEventListeners();
        this.animate();
    }

    setupThreeJS() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0e27);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.z = 20;

        // Renderer
        const canvas = document.getElementById('canvas');
        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0x00ff88, 0.8);
        pointLight.position.set(10, 10, 10);
        this.scene.add(pointLight);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupParticleSystem() {
        this.particleSystem = new ParticleSystem(this.scene, this.camera);
    }

    setupGestureDetection() {
        const videoElement = document.getElementById('video');
        this.gestureDetector = new GestureDetector(
            videoElement,
            () => this.onHandOpen(),
            () => this.onHandClosed()
        );
    }

    setupUI() {
        this.uiController = new UIController(this.particleSystem);
        this.uiController.updateStats();
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ') {
                e.preventDefault();
                this.particleSystem.triggerExplosion();
            }
        });
    }

    onHandOpen() {
        this.isHandOpen = true;
        this.particleSystem.triggerExplosion();
        this.uiController.updateGestureIndicator(true, '✋ Open Hand');
        this.uiController.updateHandStatus(true);
    }

    onHandClosed() {
        this.isHandOpen = false;
        this.uiController.updateGestureIndicator(true, '✊ Closed Hand');
        this.uiController.updateHandStatus(false);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const now = performance.now();
        this.deltaTime = now - this.lastTime;
        this.lastTime = now;

        // Update FPS
        this.uiController.updateFPS(this.uiController.calculateFPS(this.deltaTime));

        // Update particle system
        this.particleSystem.update();

        // Render
        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        const width = window.innerWidth;
        const height = window.innerHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
}

// Initialize app when document is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.app = new App();
    });
} else {
    window.app = new App();
}
