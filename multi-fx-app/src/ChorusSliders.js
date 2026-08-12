import React from "react"

import {ChorusLevelSlider} from "./ChorusLevelSlider"
import {ChorusRateSlider} from "./ChorusRateSlider"
import {ChorusDepthSlider} from "./ChorusDepthSlider"

export function ChorusSliders({
    setChorusLevel,
    setChorusRate,
    setChorusDepth
}) {
    return(
        <div className="slider-group">
            <ChorusLevelSlider 
                setChorusLevel={setChorusLevel}
            />
            <ChorusRateSlider 
                setChorusRate={setChorusRate}
            />
            <ChorusDepthSlider
                setChorusDepth={setChorusDepth}
            />
        </div>
    )
}
