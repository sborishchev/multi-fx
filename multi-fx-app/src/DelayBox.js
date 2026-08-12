import React from 'react'
import { useState } from 'react'

import { DelaySliders } from './DelaySliders'

export function DelayBox({
    level, setLevel,
    feedback, setFeedback,
    delay, setDelay,
    chosen, setChosen,
}) {
    // delay button state (live monitoring only)
    const [delayButtonState, setDelayButtonState] = useState(false);

    const startDelay = async () => {
        setDelayButtonState(!delayButtonState)

        const query = new URLSearchParams({
            delayLevel: level,
            feedback,
            delay,
            enableDelay: true,
        }).toString();
    
        try {
            const res = await fetch(`http://localhost:8000/start-effects?${query}`);
            const json = await res.json();
            console.log("Delay started:", json);
        } catch (err) {
            console.error("Failed to start delay:", err);
        }
    }; 

    const stopDelay = async () => {
        setDelayButtonState(!delayButtonState)
        try {
            const res = await fetch("http://localhost:8000/stop-effects");
          const json = await res.json();
          console.log("STOPPED:", json);
        } catch (err) {
          console.error("Failed to stop delay:", err);
        }
    };

    return(
        <div className={`effect-card${delayButtonState ? " effect-card--active" : ""}`}>
            <div className="effect-card-header">
                <div className="effect-card-title">
                    <span className={`status-dot${delayButtonState ? " status-dot--on" : ""}`} />
                    Delay
                </div>
                <button
                    className={`toggle-btn${delayButtonState ? " toggle-btn--active" : ""}`}
                    onClick={delayButtonState ? stopDelay : startDelay}
                >
                    {delayButtonState ? "Stop" : "Start"}
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
            <DelaySliders
                setDelayLevel={setLevel}
                setDelayFeedback={setFeedback}
                setDelayDelay={setDelay}
            />
        </div>
    )
}
