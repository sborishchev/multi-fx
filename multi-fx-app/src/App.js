import React, { useState } from "react"

import { EffectBoxes } from "./EffectBoxes"
import { Playback } from "./Playback"
import logo from "./logo.png"

export default function App() {
    // Distortion
    const [distortionVolume, setDistortionVolume] = useState(5);
    const [distortionGain, setDistortionGain] = useState(5);
    const [distortionWetDry, setDistortionWetDry] = useState(5);
    
    const [distortionChosen, setDistortionChosen] = useState(false);

    // Chorus
    const [chorusLevel, setChorusLevel] = useState(5);
    const [chorusRate, setChorusRate] = useState(5);
    const [chorusDepth, setChorusDepth] = useState(5);

    const [chorusChosen, setChorusChosen] = useState(false);

    // Delay
    const [delayLevel, setDelayLevel] = useState(5);
    const [delayFeedback, setDelayFeedback] = useState(5);
    const [delayDelay, setDelayDelay] = useState(5);

    const [delayChosen, setDelayChosen] = useState(false);

    const distortion = {
        volume: distortionVolume, setVolume: setDistortionVolume,
        gain: distortionGain, setGain: setDistortionGain,
        wetDry: distortionWetDry, setWetDry: setDistortionWetDry,
        chosen: distortionChosen, setChosen: setDistortionChosen,
    };
    const chorus = {
        level: chorusLevel, setLevel: setChorusLevel,
        rate: chorusRate, setRate: setChorusRate,
        depth: chorusDepth, setDepth: setChorusDepth,
        chosen: chorusChosen, setChosen: setChorusChosen,
    };
    const delay = {
        level: delayLevel, setLevel: setDelayLevel,
        feedback: delayFeedback, setFeedback: setDelayFeedback,
        delay: delayDelay, setDelay: setDelayDelay,
        chosen: delayChosen, setChosen: setDelayChosen,
    };

    return (
      <div className="app-shell">
        <div className="app-backdrop" />

        <header className="app-header">
          <img src={logo} alt="Multi FX logo" className="app-logo" />
          <h1 className="app-title">Multi<span>FX</span></h1>
        </header>

        <EffectBoxes distortion={distortion} chorus={chorus} delay={delay} />
        <Playback distortion={distortion} chorus={chorus} delay={delay} />
      </div>
    );
}
