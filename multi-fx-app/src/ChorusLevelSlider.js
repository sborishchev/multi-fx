import React from "react"
import { useState } from "react"

export function ChorusLevelSlider({
    setChorusLevel
}) {
    const [data, setData]=useState(5)

    function handleSlider(e){
        setData(e.target.value)
        setChorusLevel(e.target.value)
    }
    
    
    return(
        <div className="slider-row">
            <div className="slider-row-top">
                <span className="slider-label">Level</span>
                <span className="slider-value">{data}</span>
            </div>
            <input
                className="styled-range"
                type='range' min='0' max='10'
                step='1' value={data}
                onChange={handleSlider}
                style={{ "--fill": `${data * 10}%` }}
            />
        </div>
    )
}
