import React from 'react'
import { useState } from 'react'

import { DistortionSliders } from './DistortionSliders'

export function DistortionBox({
    volume, setVolume,
    gain, setGain,
    wetDry, setWetDry,
    chosen, setChosen,
}) {
    // distortion button state (live monitoring only)
    const [distortionButtonState, setDistortionButtonState] = useState(false);

    const startDistortion = async () => {
        setDistortionButtonState(!distortionButtonState)

        const query = new URLSearchParams({
            volume,
            gain,
            wetDry,
            enableDistortion: true,
        }).toString();

        try {
            const res = await fetch(`http://localhost:8000/start-effects?${query}`);
            const json = await res.json();
            console.log("Distortion started:", json);
        } catch (err) {
            console.error("Failed to start distortion:", err);
        }
    }; 

    const stopDistortion = async () => {
        setDistortionButtonState(!distortionButtonState)
        try {
          const res = await fetch("http://localhost:8000/stop-effects");
          const json = await res.json();
          console.log("STOPPED:", json);
        } catch (err) {
          console.error("Failed to stop distortion:", err);
        }
    };

    return(
        <div className={`effect-card${distortionButtonState ? " effect-card--active" : ""}`}>
            <div className="effect-card-header">
                <div className="effect-card-title">
                    <span className={`status-dot${distortionButtonState ? " status-dot--on" : ""}`} />
                    Distortion
                </div>
                <button
                    className={`toggle-btn${distortionButtonState ? " toggle-btn--active" : ""}`}
                    onClick={distortionButtonState ? stopDistortion : startDistortion}
                >
                    {distortionButtonState ? "Stop" : "Start"}
                </button>
            </div>
            <label className="chosen-toggle">
                <input
                    type="checkbox"
                    checked={chosen}
                    onChange={(e) => setChosen(e.target.checked)}
                />
                Include in Process Recording
            </label>
            <DistortionSliders
                setDistortionVolume={setVolume}
                setDistortionGain={setGain}
                setDistortionWetDry={setWetDry}
            />
        </div>
    )
}
