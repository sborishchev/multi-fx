import React from "react"

import {DistortionVolumeSlider} from "./DistortionVolumeSlider"
import {DistortionGainSlider} from "./DistortionGainSlider"
import {DistortionWetDrySlider} from "./DistortionWetDrySlider"


export function DistortionSliders({
    setDistortionVolume,
    setDistortionGain,
    setDistortionWetDry
}) {
    return(
        <div className="slider-group">
            <DistortionVolumeSlider 
                setDistortionVolume={setDistortionVolume}
            />
            <DistortionGainSlider 
                setDistortionGain={setDistortionGain}
            />
            <DistortionWetDrySlider
                setDistortionWetDry={setDistortionWetDry}
            />
        </div>
    )
}
