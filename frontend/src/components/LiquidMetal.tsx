"use client";

import React from "react";
import { Canvas } from "@react-three/fiber";
import { MeshDistortMaterial, Sphere, Environment, Lightformer } from "@react-three/drei";

export default function LiquidMetal() {
    return (
        <div className="fixed top-0 left-0 w-full h-full -z-10 pointer-events-none opacity-60">
            <Canvas dpr={[1, 2]}>
                <ambientLight intensity={0.5} />
                <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
                <pointLight position={[-10, -10, -10]} intensity={1} />

                <Sphere args={[1, 100, 200]} scale={2.5}>
                    <MeshDistortMaterial
                        color="#e0e0e0"
                        attach="material"
                        distort={0.6}
                        speed={3}
                        roughness={0.1}
                        metalness={1}
                    />
                </Sphere>

                <Environment preset="warehouse" />
            </Canvas>
        </div>
    );
}
