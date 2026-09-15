# Three.js Particle System Documentation

## ParticleSystem Class

### Constructor
```javascript
const particleSystem = new ParticleSystem(scene, camera);
```

### Properties
- `particleCount` - Number of particles (default: 1000)
- `color` - Particle color (THREE.Color)
- `scale` - Particle size multiplier (default: 1.5)
- `expansion` - Current expansion value
- `expansionSpeed` - Speed of expansion (default: 0.5)
- `shapeType` - Current particle formation
- `velocities` - Array of particle velocities

### Methods

#### `update()`
Update particle positions and rotations. Call in animation loop.

#### `setScale(scale)`
Set particle size scale.
```javascript
particleSystem.setScale(2.5);
```

#### `setColor(color)`
Set particle color.
```javascript
particleSystem.setColor(new THREE.Color(0xff0000));
```

#### `setExpansion(speed)`
Set expansion speed.
```javascript
particleSystem.setExpansion(1.0);
```

#### `setParticleCount(count)`
Change number of particles (regenerates geometry).
```javascript
particleSystem.setParticleCount(2000);
```

#### `setShapeType(shapeType)`
Change particle formation type.
```javascript
particleSystem.setShapeType('galaxy');
```

Available shapes: `'cube'`, `'sphere'`, `'heart'`, `'galaxy'`, `'saturn'`, `'flower'`

#### `triggerExplosion()`
Trigger particle expansion.
```javascript
particleSystem.triggerExplosion();
```

#### `reset()`
Reset particles to initial state.
```javascript
particleSystem.reset();
```

## Shape Generator Functions

Each shape has its own generator function that creates particle positions:

### Cube
Random distribution within a cube.

### Sphere
Uniform distribution on sphere surface using spherical coordinates.

### Heart
Parametric heart curve with random depth.

### Galaxy
Spiral formation with arms.

### Saturn
Combination of ring and core particles.

### Flower
Multi-petal formation.

## Performance Considerations

### Optimization Tips
1. Use BufferGeometry (already implemented)
2. Use PointsMaterial for efficient rendering
3. Limit particle count to 5000 for smooth 60+ FPS
4. Update positions directly in typed arrays
5. Batch update geometry with needsUpdate flag

### Bottlenecks
- Large particle counts (>5000)
- Complex geometries
- Frequent shape regeneration
- Heavy texture operations

## Adding Custom Shapes

1. Add case in `getParticlePosition()`:
```javascript
case 'myshape':
    pos = this.myshapePosition(t);
    break;
```

2. Implement position generator:
```javascript
myshapePosition(t) {
    return {
        x: Math.cos(t * Math.PI * 2) * 8,
        y: Math.sin(t * Math.PI * 2) * 8,
        z: (Math.random() - 0.5) * 8
    };
}
```

3. Add UI button in index.html:
```html
<button class="shape-btn" data-shape="myshape">My Shape</button>
```
