import React, { useMemo } from 'react';
import { Line, Sphere, Billboard, Text, useTexture } from '@react-three/drei';
import * as THREE from 'three';

interface CameraVizProps {
    azimuth: number;
    elevation: number;
    distance: number;
    imageUrl?: string | null;
}

export const CameraViz: React.FC<CameraVizProps> = ({ azimuth, elevation, imageUrl }) => {
    // Convert spherical coordinates to cartesian for camera position
    // Azimuth: horizontal rotation (0 is front/Z+, 90 is right/X+, 180 is back/Z-, 270 is left/X-)
    // Elevation: vertical angle

    // Convert degrees to radians
    const azRad = (azimuth * Math.PI) / 180;
    const elRad = (elevation * Math.PI) / 180;

    const r = 3; // Visual radius scale for the widget
    const cx = r * Math.cos(elRad) * Math.sin(azRad);
    const cy = r * Math.sin(elRad);
    const cz = r * Math.cos(elRad) * Math.cos(azRad);

    // Visualization colors
    const ringColor = "#00ffcc"; // Cyan/Green
    const arcColor = "#ff66cc";  // Pink
    const camColor = "#ffcc00";  // Yellow

    // Create the Azimuth Ring (Circle on XZ plane)
    const ringPoints = useMemo(() => {
        const points = [];
        for (let i = 0; i <= 64; i++) {
            const theta = (i / 64) * Math.PI * 2;
            points.push(new THREE.Vector3(Math.cos(theta) * r, 0, Math.sin(theta) * r));
        }
        return points;
    }, [r]);

    // Create the Elevation Arc
    const arcPoints = useMemo(() => {
        const points = [];
        for (let i = -45; i <= 90; i += 5) {
            const ang = (i * Math.PI) / 180;
            const ax = r * Math.cos(ang) * Math.sin(azRad);
            const ay = r * Math.sin(ang);
            const az = r * Math.cos(ang) * Math.cos(azRad);
            points.push(new THREE.Vector3(ax, ay, az));
        }
        return points;
    }, [azRad, r]);

    return (
        <group>
            {/* Azimuth Ring */}
            <Line points={ringPoints} color={ringColor} lineWidth={3} />
            <mesh position={[r * Math.sin(azRad), 0, r * Math.cos(azRad)]}>
                <sphereGeometry args={[0.2, 16, 16]} />
                <meshBasicMaterial color={ringColor} />
            </mesh>

            {/* Elevation Arc */}
            <Line points={arcPoints} color={arcColor} lineWidth={3} />

            {/* Camera Indicator */}
            <group position={[cx, cy, cz]}>
                <Sphere args={[0.3, 32, 32]}>
                    <meshStandardMaterial color={camColor} roughness={0.3} metalness={0.8} />
                </Sphere>
                {/* Camera frustum line roughly pointing to center */}
                <Line points={[new THREE.Vector3(0, 0, 0), new THREE.Vector3(-cx * 0.2, -cy * 0.2, -cz * 0.2)]} color="orange" lineWidth={1} />
            </group>

            {/* Target */}
            <Billboard position={[0, 0, 0]}>
                <mesh>
                    <planeGeometry args={[2, 2]} />
                    {imageUrl ? (
                        <ImageTexture url={imageUrl} />
                    ) : (
                        <meshBasicMaterial color="#333" />
                    )}
                </mesh>
                {!imageUrl && (
                    <Text position={[0, 0, 0.1]} fontSize={1} color="#ffcc00">
                        ☺
                    </Text>
                )}
            </Billboard>

            {/* Grid helper for floor */}
            <gridHelper args={[10, 10, 0x444444, 0x222222]} />
        </group>
    );
};

// Separate component for Texture loading
const ImageTexture = ({ url }: { url: string }) => {
    const texture = useTexture(url);
    return <meshBasicMaterial map={texture} transparent />;
};
