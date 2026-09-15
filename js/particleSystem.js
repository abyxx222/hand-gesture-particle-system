/**
 * Particle System - Manages particle generation and rendering
 * Uses Three.js Points and BufferGeometry for optimal performance
 */
class ParticleSystem {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.particles = null;
        this.geometry = null;
        this.material = null;
        this.particleCount = 1000;
        this.color = new THREE.Color(0x00ff88);
        this.scale = 1.5;
        this.expansion = 0;
        this.expansionSpeed = 0.5;
        this.shapeType = 'cube';
        this.velocities = [];
        
        this.init();
    }

    init() {
        this.createParticles();
    }

    createParticles() {
        // Clean up old particles
        if (this.particles) {
            this.scene.remove(this.particles);
            this.geometry.dispose();
            this.material.dispose();
        }

        // Create geometry
        this.geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(this.particleCount * 3);
        this.velocities = [];

        // Generate particle positions based on shape
        for (let i = 0; i < this.particleCount; i++) {
            const pos = this.getParticlePosition(i);
            positions[i * 3] = pos.x;
            positions[i * 3 + 1] = pos.y;
            positions[i * 3 + 2] = pos.z;

            this.velocities.push({
                x: (Math.random() - 0.5) * 0.02,
                y: (Math.random() - 0.5) * 0.02,
                z: (Math.random() - 0.5) * 0.02
            });
        }

        this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        // Create material
        this.material = new THREE.PointsMaterial({
            color: this.color,
            size: 0.15 * this.scale,
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true
        });

        // Create points
        this.particles = new THREE.Points(this.geometry, this.material);
        this.scene.add(this.particles);
    }

    getParticlePosition(index) {
        const pos = { x: 0, y: 0, z: 0 };
        const t = index / this.particleCount;

        switch (this.shapeType) {
            case 'sphere':
                pos = this.spherePosition(t);
                break;
            case 'heart':
                pos = this.heartPosition(t);
                break;
            case 'galaxy':
                pos = this.galaxyPosition(t);
                break;
            case 'saturn':
                pos = this.saturnPosition(t);
                break;
            case 'flower':
                pos = this.flowerPosition(t);
                break;
            default: // cube
                pos = this.cubePosition(t);
        }

        return pos;
    }

    cubePosition(t) {
        const range = 8;
        return {
            x: (Math.random() - 0.5) * range,
            y: (Math.random() - 0.5) * range,
            z: (Math.random() - 0.5) * range
        };
    }

    spherePosition(t) {
        const radius = 8;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        return {
            x: radius * Math.sin(phi) * Math.cos(theta),
            y: radius * Math.sin(phi) * Math.sin(theta),
            z: radius * Math.cos(phi)
        };
    }

    heartPosition(t) {
        const a = Math.random() * Math.PI * 2;
        const s = Math.random();
        const x = 16 * Math.sin(a) ** 3;
        const y = 13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a);
        const z = (Math.random() - 0.5) * 5;
        return {
            x: x * s * 0.3,
            y: y * s * 0.3,
            z: z * s
        };
    }

    galaxyPosition(t) {
        const angle = t * Math.PI * 12;
        const radius = 2 + t * 8;
        const z = (Math.random() - 0.5) * 4;
        return {
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
            z: z
        };
    }

    saturnPosition(t) {
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI * 2;
        
        if (Math.random() > 0.3) {
            // Ring
            const ringRadius = 5 + Math.random() * 2;
            return {
                x: Math.cos(theta) * ringRadius,
                y: (Math.random() - 0.5) * 0.5,
                z: Math.sin(theta) * ringRadius
            };
        } else {
            // Planet core
            const r = Math.random() * 2;
            return {
                x: Math.sin(phi) * Math.cos(theta) * r,
                y: Math.sin(phi) * Math.sin(theta) * r,
                z: Math.cos(phi) * r
            };
        }
    }

    flowerPosition(t) {
        const petals = 6;
        const petalIndex = Math.floor(Math.random() * petals);
        const angle = (petalIndex / petals) * Math.PI * 2 + Math.random() * 0.5;
        const distance = 1 + Math.random() * 6;
        const z = (Math.random() - 0.5) * 3;
        return {
            x: Math.cos(angle) * distance,
            y: Math.sin(angle) * distance,
            z: z
        };
    }

    update() {
        if (!this.particles) return;

        const positions = this.geometry.attributes.position.array;

        // Update particle positions with expansion
        for (let i = 0; i < this.particleCount; i++) {
            positions[i * 3] += this.velocities[i].x * this.expansion;
            positions[i * 3 + 1] += this.velocities[i].y * this.expansion;
            positions[i * 3 + 2] += this.velocities[i].z * this.expansion;
        }

        this.geometry.attributes.position.needsUpdate = true;

        // Rotate particles
        this.particles.rotation.x += 0.0002;
        this.particles.rotation.y += 0.0003;

        // Smooth expansion decay
        this.expansion *= 0.98;
    }

    setScale(scale) {
        this.scale = scale;
        this.material.size = 0.15 * scale;
    }

    setColor(color) {
        this.color = color;
        this.material.color.copy(color);
    }

    setExpansion(speed) {
        this.expansionSpeed = speed;
        this.expansion = speed;
    }

    setParticleCount(count) {
        if (this.particleCount !== count) {
            this.particleCount = count;
            this.createParticles();
        }
    }

    setShapeType(shapeType) {
        if (this.shapeType !== shapeType) {
            this.shapeType = shapeType;
            this.createParticles();
        }
    }

    triggerExplosion() {
        this.expansion = this.expansionSpeed * 2;
    }

    reset() {
        this.createParticles();
    }
}
