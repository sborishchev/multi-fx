import React from 'react'
import { useState } from 'react'

import { ChorusSliders } from './ChorusSliders'

export function ChorusBox({
    level, setLevel,
    rate, setRate,
    depth, setDepth,
    chosen, setChosen,
}) {
    // chorus button state (live monitoring only)
    const [chorusButtonState, setChorusButtonState] = useState(false);

    const startChorus = async () => {
        setChorusButtonState(!chorusButtonState)
        const query = new URLSearchParams({
            chorusLevel: level,
            chorusRate: rate,
            chorusDepth: depth,
            enableChorus: true,
        }).toString();
      
        try {
            const res = await fetch(`http://localhost:8000/start-effects?${query}`);
            const json = await res.json();
            console.log("Chorus started:", json);
        } catch (err) {
            console.error("Failed to start chorus:", err);
        }
    }; 

    const stopChorus = async () => {
        setChorusButtonState(!chorusButtonState)
        try {
          const res = await fetch("http://localhost:8000/stop-effects");
          const json = await res.json();
          console.log("STOPPED:", json);
        } catch (err) {
          console.error("Failed to stop chorus:", err);
        }
    };

    return(
        <div className={`effect-card${chorusButtonState ? " effect-card--active" : ""}`}>
            <div className="effect-card-header">
                <div className="effect-card-title">
                    <span className={`status-dot${chorusButtonState ? " status-dot--on" : ""}`} />
                    Chorus
                </div>
                <button
                    className={`toggle-btn${chorusButtonState ? " toggle-btn--active" : ""}`}
                    onClick={chorusButtonState ? stopChorus : startChorus}
                >
                    {chorusButtonState ? "Stop" : "Start"}
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
            <ChorusSliders 
                setChorusLevel={setLevel}
                setChorusRate={setRate}
                setChorusDepth={setDepth}
            />
        </div>
    )
}
