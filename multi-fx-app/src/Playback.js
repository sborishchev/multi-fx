import React, { useState } from "react"

const BACKEND_URL = "http://localhost:8000"

export function Playback({ distortion, chorus, delay }) {
    const [open, setOpen] = useState(false)
    const [version, setVersion] = useState(Date.now())
    const [isRecording, setIsRecording] = useState(false)
    const [processing, setProcessing] = useState(false)
    const [status, setStatus] = useState("")

    const refresh = () => setVersion(Date.now())

    const startRecording = async () => {
        setIsRecording(true)
        setStatus("Recording...")
        try {
            const res = await fetch(`${BACKEND_URL}/record/start`)
            const json = await res.json()
            console.log("Recording started:", json)
        } catch (err) {
            console.error("Failed to start recording:", err)
            setStatus("Failed to start recording")
        }
    }

    const stopRecording = async () => {
        setIsRecording(false)
        try {
            const res = await fetch(`${BACKEND_URL}/record/stop`)
            const json = await res.json()
            console.log("Recording stopped:", json)
            setStatus("Recording saved")
            refresh()
        } catch (err) {
            console.error("Failed to stop recording:", err)
            setStatus("Failed to stop recording")
        }
    }

    const processRecording = async () => {
        setProcessing(true)
        setStatus("Processing...")

        const query = new URLSearchParams({
            volume: distortion.chosen ? distortion.volume : 0,
            gain: distortion.chosen ? distortion.gain : 0,
            wetDry: distortion.chosen ? distortion.wetDry : 0,
            enableDistortion: distortion.chosen,
            chorusLevel: chorus.chosen ? chorus.level : 0,
            chorusRate: chorus.chosen ? chorus.rate : 0,
            chorusDepth: chorus.chosen ? chorus.depth : 0,
            enableChorus: chorus.chosen,
            delayLevel: delay.chosen ? delay.level : 0,
            feedback: delay.chosen ? delay.feedback : 0,
            delay: delay.chosen ? delay.delay : 0,
            enableDelay: delay.chosen,
        }).toString()

        try {
            const res = await fetch(`${BACKEND_URL}/process-recording?${query}`)
            const json = await res.json()
            if (res.ok) {
                console.log("Processed:", json)
                setStatus("Processed recording ready")
                refresh()
            } else {
                console.error("Failed to process recording:", json)
                setStatus(json.error || "Failed to process recording")
            }
        } catch (err) {
            console.error("Failed to process recording:", err)
            setStatus("Failed to process recording")
        } finally {
            setProcessing(false)
        }
    }

    const anyChosen = distortion.chosen || chorus.chosen || delay.chosen

    return (
        <>
            <button
                className={`recordings-tab${open ? " recordings-tab--open" : ""}`}
                onClick={() => setOpen(!open)}
            >
                Recordings
            </button>

            {open && <div className="recordings-overlay" onClick={() => setOpen(false)} />}

            <aside className={`recordings-drawer${open ? " recordings-drawer--open" : ""}`}>
                <div className="playback-header">
                    <h3>Recordings</h3>
                    <button className="drawer-close" onClick={() => setOpen(false)} aria-label="Close">
                        &times;
                    </button>
                </div>
                <div className="playback-actions">
                    <button
                        className={`toggle-btn${isRecording ? " toggle-btn--active" : ""}`}
                        onClick={isRecording ? stopRecording : startRecording}
                    >
                        {isRecording ? "Stop Recording" : "Record"}
                    </button>
                    <button
                        className="toggle-btn"
                        onClick={processRecording}
                        disabled={processing || !anyChosen}
                    >
                        {processing ? "Processing..." : "Process Recording"}
                    </button>
                </div>
                <p className="playback-hint">
                    Click Record, make some noise, then Stop Recording to
                    capture the dry (unprocessed) input. Check "Include in
                    Process Recording" on any effect card, then hit Process
                    Recording here to apply all of them together to the wet
                    (processed) output.
                    {status && <><br />{status}</>}
                </p>
                <div className="playback-row">
                    <span className="slider-label">Dry (input)</span>
                    <audio
                        key={`dry-${version}`}
                        controls
                        src={`${BACKEND_URL}/recordings/dry?v=${version}`}
                    />
                </div>
                <div className="playback-row">
                    <span className="slider-label">Wet (processed)</span>
                    <audio
                        key={`wet-${version}`}
                        controls
                        src={`${BACKEND_URL}/recordings/wet?v=${version}`}
                    />
                </div>
            </aside>
        </>
    )
}
