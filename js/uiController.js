/**
 * UI Controller - Manages all UI interactions and state updates
 */
class UIController {
    constructor(particleSystem) {
        this.particleSystem = particleSystem;
        this.currentShape = 'cube';
        this.currentColor = '#00ff88';
        this.fps = 0;
        this.frameCount = 0;
        this.lastTime = performance.now();
        
        this.init();
    }

    init() {
        this.setupShapeButtons();
        this.setupColorPicker();
        this.setupSliders();
        this.setupButtons();
        this.startFPSCounter();
    }

    setupShapeButtons() {
        document.querySelectorAll('.shape-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Remove active class from all buttons
                document.querySelectorAll('.shape-btn').forEach(b => b.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                const shape = e.target.dataset.shape;
                this.currentShape = shape;
                this.particleSystem.setShapeType(shape);
            });
        });
    }

    setupColorPicker() {
        const colorPicker = document.getElementById('colorPicker');
        const colorValue = document.getElementById('colorValue');

        colorPicker.addEventListener('input', (e) => {
            this.currentColor = e.target.value;
            colorValue.textContent = this.currentColor;
            this.particleSystem.setColor(new THREE.Color(this.currentColor));
        });
    }

    setupSliders() {
        // Scale slider
        const scaleSlider = document.getElementById('scaleSlider');
        const scaleValue = document.getElementById('scaleValue');
        scaleSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            scaleValue.textContent = value.toFixed(1);
            this.particleSystem.setScale(value);
        });

        // Expansion speed slider
        const expansionSlider = document.getElementById('expansionSlider');
        const expansionValue = document.getElementById('expansionValue');
        expansionSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            expansionValue.textContent = value.toFixed(1);
            this.particleSystem.expansionSpeed = value;
        });

        // Particle count slider
        const countSlider = document.getElementById('countSlider');
        const countValue = document.getElementById('countValue');
        countSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            countValue.textContent = value;
            this.particleSystem.setParticleCount(value);
        });
    }

    setupButtons() {
        // Reset button
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.particleSystem.reset();
            this.updateStats();
        });

        // Fullscreen button
        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.error(`Error attempting to enable fullscreen: ${err.message}`);
                });
            } else {
                document.exitFullscreen();
            }
        });
    }

    updateStats() {
        document.getElementById('particle-count').textContent = this.particleSystem.particleCount;
    }

    updateFPS(fps) {
        this.fps = fps;
        document.getElementById('fps').textContent = Math.round(fps);
    }

    updateHandStatus(isOpen) {
        const status = isOpen ? 'Yes' : 'No';
        document.getElementById('hand-open').textContent = status;
    }

    updateGestureIndicator(isDetected, gestureType = 'Scanning...') {
        const dot = document.getElementById('gesture-dot');
        const text = document.getElementById('gesture-text');
        
        if (isDetected) {
            dot.classList.add('active');
            text.textContent = gestureType;
        } else {
            dot.classList.remove('active');
            text.textContent = 'Scanning...';
        }
    }

    startFPSCounter() {
        setInterval(() => {
            // FPS will be updated via the animation loop
        }, 1000);
    }

    calculateFPS(deltaTime) {
        if (deltaTime > 0) {
            return 1000 / deltaTime;
        }
        return 0;
    }
}
