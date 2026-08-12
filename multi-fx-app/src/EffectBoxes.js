import React from "react";

import { DelayBox } from "./DelayBox";
import { ChorusBox } from "./ChorusBox";
import { DistortionBox } from "./DistortionBox";

export function EffectBoxes({ distortion, chorus, delay }) {
    return (
        <>  
            <div className="effect-boxes">
                <DelayBox {...delay} />
                <ChorusBox {...chorus} />
                <DistortionBox {...distortion} />
            </div>
        </>
    )
}
