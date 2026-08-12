import React from "react"

import {DelayLevelSlider} from "./DelayLevelSlider"
import {DelayFeedbackSlider} from "./DelayFeedbackSlider"
import {DelayDelaySlider} from "./DelayDelaySlider"

export function DelaySliders({
    setDelayLevel,
    setDelayFeedback,
    setDelayDelay
}) {
    return(
        <div className="slider-group">
            <DelayLevelSlider 
                setDelayLevel={setDelayLevel}
            />
            <DelayFeedbackSlider 
                setDelayFeedback={setDelayFeedback}
            />
            <DelayDelaySlider
                setDelayDelay={setDelayDelay}
            />
        </div>
    )
}
