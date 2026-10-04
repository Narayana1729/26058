import React, { useState, useEffect, useRef } from 'react';
import { 
  Waves, 
  Activity, 
  Sliders, 
  Compass, 
  Copy, 
  Check, 
  Volume2, 
  BookOpen, 
  X
} from 'lucide-react';

export default function App() {
  // Environmental & DSP State
  const [turbidity, setTurbidity] = useState(15);
  const [salinity, setSalinity] = useState(35);
  const [depth, setDepth] = useState(25);
  const [temperature, setTemperature] = useState(15);
  const [tukeyAlpha, setTukeyAlpha] = useState(0.25);
  const [sampleClock, setSampleClock] = useState(100); // in kHz

  // UI State
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showGuideModal, setShowGuideModal] = useState(false);

  // Canvas Refs
  const waveCanvasRef = useRef(null);
  const fftCanvasRef = useRef(null);
  const fgCanvasRef = useRef(null);
  const tlCanvasRef = useRef(null);

  // Audio Context Ref
  const audioCtxRef = useRef(null);

  // 1. Mackenzie (1981) Equation for Speed of Sound (m/s)
  const calcMackenzieSpeed = (T, S, D) => {
    return (
      1448.96 +
      4.591 * T -
      5.304e-2 * Math.pow(T, 2) +
      2.374e-4 * Math.pow(T, 3) +
      1.340 * (S - 35) +
      1.630e-2 * D +
      1.675e-7 * Math.pow(D, 2) -
      1.025e-2 * T * (S - 35) -
      7.139e-13 * T * Math.pow(D, 3)
    );
  };

  // 2. Francois-Garrison (1982) Ocean Sound Absorption Engine
  const calcFrancoisGarrisonAlpha = (f_khz, S, T, D_m, c, pH = 8.0) => {
    const T_kelvin = T + 273.15;
    
    // Boric Acid relaxation
    const f1 = 2.8 * Math.sqrt(S / 35.0) * Math.pow(10.0, 4.0 - 1245.0 / T_kelvin);
    const P1 = 1.0;
    const A1 = (8.86 / c) * Math.pow(10.0, 0.78 * pH - 5.0);
    const alpha_boric = (A1 * P1 * f1 * f_khz * f_khz) / (f1 * f1 + f_khz * f_khz);
    
    // Magnesium Sulfate (MgSO4) relaxation
    const f2 = (8.17 * Math.pow(10.0, 8.0 - 1990.0 / T_kelvin)) / (1.0 + 0.0018 * (S - 35.0));
    const P2 = 1.0 - 1.37e-4 * D_m + 6.2e-9 * D_m * D_m;
    const A2 = 21.44 * (S / c) * (1.0 + 0.025 * T);
    const alpha_mgso4 = (A2 * P2 * f2 * f_khz * f_khz) / (f2 * f2 + f_khz * f_khz);
    
    // Pure Water Viscous Attenuation
    const P3 = 1.0 - 3.83e-5 * D_m + 4.9e-10 * D_m * D_m;
    let A3 = 0;
    if (T <= 20.0) {
      A3 = 4.937e-4 - 2.59e-5 * T + 9.11e-7 * T * T - 1.50e-8 * Math.pow(T, 3);
    } else {
      A3 = 3.964e-4 - 1.146e-5 * T + 1.45e-7 * T * T - 6.5e-10 * Math.pow(T, 3);
    }
    const alpha_water = A3 * P3 * f_khz * f_khz;
    
    return {
      boric: alpha_boric,
      mgso4: alpha_mgso4,
      water: alpha_water,
      total: alpha_boric + alpha_mgso4 + alpha_water // dB / km
    };
  };

  const fs_hz = sampleClock * 1000;
  const speedOfSound = calcMackenzieSpeed(temperature, salinity, depth);
  const SAMPLES = 512;
  const maxSafeFreq = Math.floor(fs_hz * 0.42);

  // Mode Decision Parameters
  let modeNumber = 1;
  let modeName = 'Mode 1: Balanced Coastal (250 kHz Carrier)';
  let modeBadgeBg = 'var(--honey-light)';
  let modeBadgeText = 'var(--honey-amber)';
  let modeBadgeBorder = 'var(--honey-border)';
  let f0 = 1000, f1 = Math.min(18000, maxSafeFreq);
  let tim6_arr = Math.round(84000000 / fs_hz - 1);
  let carrierFreq = '250 kHz';
  let modeRationale = 'Balanced ocean conditions: optimized tradeoff between resolution and penetration.';

  if (turbidity < 25) {
    modeNumber = 0;
    modeName = 'Mode 0: Clear Water (450 kHz Carrier)';
    modeBadgeBg = 'var(--mint-light)';
    modeBadgeText = 'var(--mint-green)';
    modeBadgeBorder = 'var(--mint-border)';
    f0 = 2000;
    f1 = Math.min(25000, maxSafeFreq);
    carrierFreq = '450 kHz';
    modeRationale = 'Low turbidity allows high frequency 450 kHz acoustic imaging with millimeter precision.';
  } else if (turbidity > 90) {
    modeNumber = 2;
    modeName = 'Mode 2: Turbid / Muddy (100 kHz Carrier)';
    modeBadgeBg = 'var(--rose-light)';
    modeBadgeText = 'var(--soft-rose)';
    modeBadgeBorder = 'var(--rose-border)';
    f0 = 500;
    f1 = Math.min(8000, maxSafeFreq);
    carrierFreq = '100 kHz';
    modeRationale = 'Suspended mud particles scatter high frequencies; downshifting to 100 kHz preserves long range.';
  }

  // Synthesize 512 Samples
  const Tp = SAMPLES / fs_hz;
  const B = f1 - f0;
  const samples = [];
  for (let i = 0; i < SAMPLES; i++) {
    const t = i / fs_hz;
    let w = 1.0;
    if (tukeyAlpha > 0) {
      const edge = tukeyAlpha / 2.0;
      const pos = i / (SAMPLES - 1);
      if (pos < edge) {
        w = 0.5 * (1 + Math.cos(Math.PI * ((2 * pos / tukeyAlpha) - 1)));
      } else if (pos > 1 - edge) {
        w = 0.5 * (1 + Math.cos(Math.PI * ((2 * pos / tukeyAlpha) - (2 / tukeyAlpha) + 1)));
      }
    }
    const s = Math.sin(2 * Math.PI * f0 * t + Math.PI * (B / Tp) * t * t) * w;
    const dac = Math.round(2047.5 * (1.0 + s));
    samples.push(Math.max(0, Math.min(4095, dac)));
  }

  // Audio Sonification Player
  const playChirpSound = () => {
    try {
      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      if (ctx.state === 'suspended') ctx.resume();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      
      const duration = 0.35;
      const now = ctx.currentTime;
      const audioF0 = Math.max(300, f0 / 4);
      const audioF1 = Math.min(4500, f1 / 4);

      osc.type = 'sine';
      osc.frequency.setValueAtTime(audioF0, now);
      osc.frequency.linearRampToValueAtTime(audioF1, now + duration);

      // Dynamically shape amplitude envelope using exact Tukey Window Alpha
      // alpha = 0: Hard rectangular edges (clicks/pops)
      // alpha = 1.0: Full Hann cosine smooth taper
      const taperTime = Math.max(0.001, (tukeyAlpha / 2) * duration);
      
      if (tukeyAlpha <= 0.05) {
        // Rectangular window: sharp start and abrupt cutoff (clicks)
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.setValueAtTime(0.2, now + duration - 0.002);
        gain.gain.linearRampToValueAtTime(0.001, now + duration);
      } else {
        // Tapered Tukey window: smooth cosine-like attack & decay
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.2, now + taperTime);
        gain.gain.setValueAtTime(0.2, now + duration - taperTime);
        gain.gain.linearRampToValueAtTime(0.001, now + duration);
      }

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + duration);
      setIsPlayingAudio(true);
      setTimeout(() => setIsPlayingAudio(false), duration * 1000);
    } catch (e) {
      console.error('Audio error:', e);
    }
  };

  // Render Minimalist Canvases
  useEffect(() => {
    // 1. Time Domain Waveform
    if (waveCanvasRef.current) {
      const cv = waveCanvasRef.current;
      const ctx = cv.getContext('2d');
      const w = cv.width, h = cv.height;
      ctx.clearRect(0, 0, w, h);

      // Clean Light Grid
      ctx.strokeStyle = '#F1F5F9';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let y = 20; y < h; y += 28) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
      for (let x = 40; x < w; x += 55) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
      ctx.stroke();

      // Midline
      ctx.strokeStyle = '#E2E8F0';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2);
      ctx.stroke();
      ctx.setLineDash([]);

      // Subtle Lavender Gradient Fill
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, 'rgba(124, 58, 237, 0.12)');
      grad.addColorStop(1, 'rgba(124, 58, 237, 0.0)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.moveTo(0, h / 2);
      for (let i = 0; i < samples.length; i++) {
        const x = (i / (samples.length - 1)) * w;
        const y = h - (samples[i] / 4095) * (h - 20) - 10;
        ctx.lineTo(x, y);
      }
      ctx.lineTo(w, h / 2);
      ctx.closePath();
      ctx.fill();

      // Wave Trace
      ctx.strokeStyle = '#7C3AED';
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      for (let i = 0; i < samples.length; i++) {
        const x = (i / (samples.length - 1)) * w;
        const y = h - (samples[i] / 4095) * (h - 20) - 10;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Labels
      ctx.fillStyle = '#94A3B8';
      ctx.font = '10px Inter';
      ctx.fillText('+3.3V (4095)', 8, 14);
      ctx.fillText('+1.65V (2048)', 8, h / 2 - 4);
      ctx.fillText('0.0V (0)', 8, h - 4);
    }

    // 2. Computed 512-pt DFT Canvas
    if (fftCanvasRef.current) {
      const cv = fftCanvasRef.current;
      const ctx = cv.getContext('2d');
      const w = cv.width, h = cv.height;
      ctx.clearRect(0, 0, w, h);

      ctx.strokeStyle = '#F1F5F9';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let y = 20; y < h; y += 28) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
      for (let x = 40; x < w; x += 55) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
      ctx.stroke();

      const N = samples.length;
      const numBins = Math.floor(N / 2);
      const mag = new Float32Array(numBins);
      let maxMag = 1e-6;

      const x_ac = new Float32Array(N);
      let mean = 0;
      for (let i = 0; i < N; i++) mean += samples[i];
      mean /= N;
      for (let i = 0; i < N; i++) x_ac[i] = samples[i] - mean;

      for (let k = 0; k < numBins; k++) {
        let real = 0, imag = 0;
        const angleStep = (2 * Math.PI * k) / N;
        for (let n = 0; n < N; n++) {
          const angle = angleStep * n;
          real += x_ac[n] * Math.cos(angle);
          imag -= x_ac[n] * Math.sin(angle);
        }
        const m = Math.sqrt(real * real + imag * imag);
        mag[k] = m;
        if (m > maxMag) maxMag = m;
      }

      // Soft Mint Gradient Fill
      const grad = ctx.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, 'rgba(5, 150, 105, 0.15)');
      grad.addColorStop(1, 'rgba(5, 150, 105, 0.0)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.moveTo(0, h);
      for (let k = 0; k < numBins; k++) {
        const freq_k = (k * fs_hz) / N;
        const x = (freq_k / (fs_hz / 2)) * w;
        const db = 20 * Math.log10(Math.max(1e-4, mag[k] / maxMag));
        const normalizedY = Math.max(0, (db + 60) / 60);
        const y = h - 15 - normalizedY * (h - 35);
        ctx.lineTo(x, y);
      }
      ctx.lineTo(w, h);
      ctx.closePath();
      ctx.fill();

      // Spectrum Trace
      ctx.strokeStyle = '#059669';
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      for (let k = 0; k < numBins; k++) {
        const freq_k = (k * fs_hz) / N;
        const x = (freq_k / (fs_hz / 2)) * w;
        const db = 20 * Math.log10(Math.max(1e-4, mag[k] / maxMag));
        const normalizedY = Math.max(0, (db + 60) / 60);
        const y = h - 15 - normalizedY * (h - 35);
        if (k === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      ctx.fillStyle = '#059669';
      ctx.font = '10px Inter';
      ctx.fillText(`Passband: ${(f0/1000).toFixed(1)}k - ${(f1/1000).toFixed(1)}kHz (Nyquist: ${(fs_hz/2000).toFixed(0)}kHz)`, 8, 14);
      ctx.fillStyle = '#94A3B8';
      ctx.fillText('0 dB (Peak)', w - 70, 20);
      ctx.fillText('-40 dB Sidelobes', w - 95, h - 25);
    }

    // 3. Francois-Garrison Absorption Canvas
    if (fgCanvasRef.current) {
      const cv = fgCanvasRef.current;
      const ctx = cv.getContext('2d');
      const w = cv.width, h = cv.height;
      ctx.clearRect(0, 0, w, h);

      // Clean Dark Grid & Axes
      ctx.strokeStyle = '#E2E8F0';
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      // Y Grid (dB/km)
      for (let yVal = 0; yVal <= 200; yVal += 50) {
        const y = h - 22 - (yVal / 220) * (h - 35);
        ctx.moveTo(35, y); ctx.lineTo(w - 10, y);
      }
      // X Grid (kHz)
      const xFreqs = [10, 100, 250, 400, 500];
      xFreqs.forEach(freq => {
        const x = 35 + ((freq - 10) / 490) * (w - 45);
        ctx.moveTo(x, 8); ctx.lineTo(x, h - 22);
      });
      ctx.stroke();

      // Axis Labels & Numbers
      ctx.fillStyle = '#94A3B8';
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'right';
      for (let yVal = 0; yVal <= 200; yVal += 100) {
        const y = h - 22 - (yVal / 220) * (h - 35);
        ctx.fillText(`${yVal}`, 30, y + 3);
      }
      ctx.textAlign = 'center';
      xFreqs.forEach(freq => {
        const x = 35 + ((freq - 10) / 490) * (w - 45);
        ctx.fillText(`${freq}k`, x, h - 8);
      });

      // Absorption Curve
      const isHighTurb = turbidity > 80;
      const strokeColor = isHighTurb ? '#E11D48' : '#6366F1';
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      
      for (let f = 10; f <= 500; f += 5) {
        const fg = calcFrancoisGarrisonAlpha(f, salinity, temperature, depth, speedOfSound);
        const a_turb_penalty = 0.00085 * turbidity * Math.pow(f / 100.0, 1.35) * 1000.0;
        const total = Math.min(220, fg.total + a_turb_penalty);

        const x = 35 + ((f - 10) / 490) * (w - 45);
        const y = h - 22 - (total / 220) * (h - 35);
        if (f === 10) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // Badge Top Overlay
      const fg100 = calcFrancoisGarrisonAlpha(100, salinity, temperature, depth, speedOfSound);
      const a100 = (fg100.total + 0.00085 * turbidity * 1000).toFixed(1);
      ctx.textAlign = 'left';
      ctx.fillStyle = '#0F172A';
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.fillText(`α(100kHz) = ${a100} dB/km`, 42, 20);
      ctx.fillStyle = isHighTurb ? '#E11D48' : '#64748B';
      ctx.font = '9px Inter, sans-serif';
      ctx.fillText(`(Mud Penalty: +${(0.00085 * turbidity * 1000).toFixed(1)} dB/km)`, 42, 33);
    }

    // 4. Transmission Loss Canvas (Crystal Clear Readability)
    if (tlCanvasRef.current) {
      const cv = tlCanvasRef.current;
      const ctx = cv.getContext('2d');
      const w = cv.width, h = cv.height;
      ctx.clearRect(0, 0, w, h);

      // Y-axis: 0 to 120 dB, X-axis: 10m to 500m
      const xMargin = 35, yMargin = 22;
      const plotW = w - xMargin - 10;
      const plotH = h - yMargin - 12;

      // Blind Zone Background (>80 dB)
      const yThresh = h - yMargin - (80 / 120) * plotH;
      ctx.fillStyle = 'rgba(254, 226, 226, 0.45)'; // Light red blind zone
      ctx.fillRect(xMargin, 12, plotW, yThresh - 12);
      ctx.fillStyle = 'rgba(240, 253, 244, 0.45)'; // Light green safe zone
      ctx.fillRect(xMargin, yThresh, plotW, h - yMargin - yThresh);

      // Grid Lines
      ctx.strokeStyle = '#E2E8F0';
      ctx.lineWidth = 0.8;
      ctx.beginPath();
      // Y Grid
      for (let loss = 0; loss <= 120; loss += 40) {
        const y = h - yMargin - (loss / 120) * plotH;
        ctx.moveTo(xMargin, y); ctx.lineTo(w - 10, y);
      }
      // X Grid
      const xDistances = [50, 150, 300, 500];
      xDistances.forEach(dist => {
        const x = xMargin + ((dist - 10) / 490) * plotW;
        ctx.moveTo(x, 12); ctx.lineTo(x, h - yMargin);
      });
      ctx.stroke();

      // Axis Labels
      ctx.fillStyle = '#94A3B8';
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'right';
      for (let loss = 0; loss <= 120; loss += 40) {
        const y = h - yMargin - (loss / 120) * plotH;
        ctx.fillText(`${loss}dB`, xMargin - 4, y + 3);
      }
      ctx.textAlign = 'center';
      xDistances.forEach(dist => {
        const x = xMargin + ((dist - 10) / 490) * plotW;
        ctx.fillText(`${dist}m`, x, h - 8);
      });

      // 80 dB Detection Threshold Line
      ctx.strokeStyle = '#DC2626';
      ctx.lineWidth = 1.4;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(xMargin, yThresh); ctx.lineTo(w - 10, yThresh);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Place 80dB label on right edge so it never collides with curves on left
      ctx.fillStyle = '#DC2626';
      ctx.font = 'bold 9px Inter, sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText('80 dB Ceiling', w - 12, yThresh - 4);

      const fg100 = calcFrancoisGarrisonAlpha(100, salinity, temperature, depth, speedOfSound);
      const fg450 = calcFrancoisGarrisonAlpha(450, salinity, temperature, depth, speedOfSound);

      const a100_per_m = (fg100.total + 0.00085 * turbidity * Math.pow(1.0, 1.35) * 1000.0) / 1000.0;
      const a450_per_m = (fg450.total + 0.00085 * turbidity * Math.pow(4.5, 1.35) * 1000.0) / 1000.0;

      // 100 kHz (Blue Line - Deep Penetration)
      ctx.strokeStyle = '#2563EB';
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      for (let r = 10; r <= 500; r += 5) {
        const tl = Math.min(120, 20 * Math.log10(r) + a100_per_m * r);
        const x = xMargin + ((r - 10) / 490) * plotW;
        const y = h - yMargin - (tl / 120) * plotH;
        if (r === 10) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      // 450 kHz (Red Line - High Res)
      ctx.strokeStyle = '#E11D48';
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      let crossX = null, crossY = null, crossDist = null;
      for (let r = 10; r <= 500; r += 5) {
        const tl = 20 * Math.log10(r) + a450_per_m * r;
        const clampedTl = Math.min(120, tl);
        const x = xMargin + ((r - 10) / 490) * plotW;
        const y = h - yMargin - (clampedTl / 120) * plotH;
        if (r === 10) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);

        // Find 80dB crossing point
        if (tl >= 80 && crossDist === null) {
          crossDist = r;
          crossX = x;
          crossY = yThresh;
        }
      }
      ctx.stroke();

      // Draw Crossing Marker & Clean Callout Pill for 450 kHz
      if (crossX && crossDist < 500) {
        // Red dot
        ctx.fillStyle = '#E11D48';
        ctx.beginPath();
        ctx.arc(crossX, crossY, 4.5, 0, 2 * Math.PI);
        ctx.fill();

        // Callout Pill
        const pillText = `Blind @ ${crossDist}m`;
        ctx.font = 'bold 9px Inter, sans-serif';
        const textWidth = ctx.measureText(pillText).width;
        const pillX = Math.max(xMargin + textWidth / 2 + 6, Math.min(crossX, w - textWidth / 2 - 20));
        const pillY = yThresh - 9;
        
        ctx.fillStyle = '#E11D48';
        ctx.fillRect(pillX - textWidth / 2 - 5, pillY - 10, textWidth + 10, 13);
        
        ctx.fillStyle = '#FFFFFF';
        ctx.textAlign = 'center';
        ctx.fillText(pillText, pillX, pillY);
      }
    }
  }, [turbidity, salinity, depth, temperature, tukeyAlpha, sampleClock, speedOfSound]);

  const handleCopyCode = () => {
    const code = `// 512-Point 12-bit Tukey LFM Chirp Array
#include <stdint.h>
#define CHIRP_SAMPLES 512
static const uint16_t chirp_lfm_tukey[CHIRP_SAMPLES] = {
  ${samples.join(', ')}
};`;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const setEnvironmentPreset = (type) => {
    if (type === 'clear') {
      setTurbidity(8); setSalinity(35); setDepth(20); setTemperature(24);
    } else if (type === 'muddy') {
      setTurbidity(160); setSalinity(28); setDepth(12); setTemperature(26);
    } else if (type === 'deep') {
      setTurbidity(5); setSalinity(35); setDepth(350); setTemperature(4);
    } else if (type === 'fresh') {
      setTurbidity(40); setSalinity(0); setDepth(8); setTemperature(20);
    }
  };

  const currentFG = calcFrancoisGarrisonAlpha(100, salinity, temperature, depth, speedOfSound);

  return (
    <div style={{ padding: '28px 36px', maxWidth: '1440px', margin: '0 auto' }}>
      
      {/* MINIMALIST CLEAN WHITE HEADER */}
      <header className="minimal-panel" style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '16px 24px',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ 
            width: '42px', 
            height: '42px', 
            borderRadius: '10px', 
            background: 'var(--lavender-light)',
            border: '1px solid var(--lavender-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--lavender-primary)'
          }}>
            <Waves size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 className="font-heading" style={{ fontSize: '1.25rem', fontWeight: '800', color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
                Software-Defined Sonar Dashboard
              </h1>
              <span style={{ 
                background: 'var(--lavender-light)', 
                color: 'var(--lavender-primary)', 
                border: '1px solid var(--lavender-border)',
                padding: '2px 8px', 
                borderRadius: '6px', 
                fontSize: '0.72rem', 
                fontWeight: '700' 
              }}>
                Dual-Layer SDR
              </span>
            </div>
            <div style={{ display: 'flex', gap: '16px', fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              <span>Francois-Garrison (1982) Model</span>
              <span>•</span>
              <span>Mackenzie Speed of Sound: <b style={{ color: 'var(--lavender-primary)' }}>{speedOfSound.toFixed(1)} m/s</b></span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button 
            onClick={playChirpSound}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: isPlayingAudio ? 'var(--mint-light)' : 'var(--lavender-light)',
              border: `1px solid ${isPlayingAudio ? 'var(--mint-border)' : 'var(--lavender-border)'}`,
              color: isPlayingAudio ? 'var(--mint-green)' : 'var(--lavender-primary)',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '0.84rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <Volume2 size={16} />
            {isPlayingAudio ? 'Playing Chirp...' : 'Audible Chirp Demo'}
          </button>

          <button 
            onClick={() => setShowGuideModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: '#F8FAFC',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '0.84rem',
              cursor: 'pointer'
            }}
          >
            <BookOpen size={16} />
            Architecture Guide
          </button>
        </div>
      </header>

      {/* QUICK PRESETS ROW */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '10px', 
        marginBottom: '20px',
        padding: '10px 16px',
        background: '#FFFFFF',
        borderRadius: '10px',
        border: '1px solid var(--border-color)'
      }}>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: '600' }}>Ocean Presets:</span>
        <button onClick={() => setEnvironmentPreset('clear')} style={{ background: 'var(--mint-light)', border: '1px solid var(--mint-border)', color: 'var(--mint-green)', padding: '4px 12px', borderRadius: '6px', fontSize: '0.78rem', fontWeight: '600', cursor: 'pointer' }}>🏝️ Clear Reef (450 kHz)</button>
        <button onClick={() => setEnvironmentPreset('muddy')} style={{ background: 'var(--rose-light)', border: '1px solid var(--rose-border)', color: 'var(--soft-rose)', padding: '4px 12px', borderRadius: '6px', fontSize: '0.78rem', fontWeight: '600', cursor: 'pointer' }}>🚢 Muddy Port (100 kHz)</button>
        <button onClick={() => setEnvironmentPreset('deep')} style={{ background: 'var(--periwinkle-light)', border: '1px solid #C7D2FE', color: 'var(--periwinkle)', padding: '4px 12px', borderRadius: '6px', fontSize: '0.78rem', fontWeight: '600', cursor: 'pointer' }}>❄️ Deep Trench (4°C, 350m)</button>
        <button onClick={() => setEnvironmentPreset('fresh')} style={{ background: 'var(--honey-light)', border: '1px solid var(--honey-border)', color: 'var(--honey-amber)', padding: '4px 12px', borderRadius: '6px', fontSize: '0.78rem', fontWeight: '600', cursor: 'pointer' }}>🏞️ Fresh River (0 PSU)</button>
      </div>

      {/* 3-COLUMN MASTER GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 1fr', gap: '20px' }}>
        
        {/* ================= COLUMN 1: CONTROLS & DECISION ================= */}
        <div className="minimal-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--lavender-primary)', fontWeight: '700', fontSize: '0.92rem' }}>
            <Sliders size={16} />
            <span>Environmental Parameters</span>
          </div>

          {/* Sliders */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Turbidity (Murkiness / Mud)</span>
              <span className="font-mono" style={{ color: turbidity > 90 ? 'var(--soft-rose)' : 'var(--mint-green)', fontWeight: '700' }}>{turbidity} NTU</span>
            </div>
            <input type="range" min="0" max="250" value={turbidity} onChange={e => setTurbidity(Number(e.target.value))} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Salinity (Dissolved Salt)</span>
              <span className="font-mono" style={{ color: 'var(--lavender-primary)', fontWeight: '700' }}>{salinity} PSU</span>
            </div>
            <input type="range" min="0" max="40" value={salinity} onChange={e => setSalinity(Number(e.target.value))} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Water Depth (Pressure)</span>
              <span className="font-mono" style={{ color: 'var(--lavender-primary)', fontWeight: '700' }}>{depth} m</span>
            </div>
            <input type="range" min="0" max="500" value={depth} onChange={e => setDepth(Number(e.target.value))} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Water Temperature</span>
              <span className="font-mono" style={{ color: 'var(--lavender-primary)', fontWeight: '700' }}>{temperature} °C</span>
            </div>
            <input type="range" min="2" max="35" value={temperature} onChange={e => setTemperature(Number(e.target.value))} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Tukey Window Alpha</span>
              <span className="font-mono" style={{ color: 'var(--lavender-primary)', fontWeight: '700' }}>{tukeyAlpha.toFixed(2)}</span>
            </div>
            <input type="range" min="0" max="1" step="0.05" value={tukeyAlpha} onChange={e => setTukeyAlpha(Number(e.target.value))} />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Sampling Clock (fs)</span>
              <span className="font-mono" style={{ color: 'var(--lavender-primary)', fontWeight: '700' }}>{sampleClock} kHz</span>
            </div>
            <input type="range" min="50" max="200" value={sampleClock} onChange={e => setSampleClock(Number(e.target.value))} />
          </div>

          {/* SOFT PASTEL STM32 DECISION ENGINE CARD */}
          <div style={{ 
            marginTop: '6px', 
            padding: '14px', 
            borderRadius: '8px', 
            border: `1px solid ${modeBadgeBorder}`, 
            background: modeBadgeBg
          }}>
            <div style={{ fontSize: '0.72rem', fontWeight: '700', color: modeBadgeText, textTransform: 'uppercase', marginBottom: '2px' }}>
              Autonomous STM32 Decision
            </div>
            <div className="font-heading" style={{ fontSize: '0.92rem', fontWeight: '700', color: modeBadgeText, marginBottom: '6px' }}>
              {modeName}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.45' }}>
              <div>• <b>Baseband Chirp</b>: <span className="font-mono">{(f0/1000).toFixed(1)}k – {(f1/1000).toFixed(1)}kHz</span> (DAC)</div>
              <div>• <b>Acoustic Carrier</b>: <span className="font-mono">{carrierFreq}</span> (Transducer)</div>
              <div>• <b>Hardware Timer</b>: <code className="font-mono" style={{ background: '#FFFFFF', padding: '2px 6px', borderRadius: '4px', border: '1px solid #E2E8F0' }}>TIM6-&gt;ARR = {tim6_arr}</code></div>
              <div style={{ marginTop: '4px', color: 'var(--text-muted)', fontSize: '0.75rem' }}>{modeRationale}</div>
            </div>
          </div>
        </div>

        {/* ================= COLUMN 2: DAY 1 DSP & FFT SPECTRUM ================= */}
        <div className="minimal-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)', fontWeight: '700', fontSize: '0.92rem' }}>
              <Activity size={16} color="var(--lavender-primary)" />
              <span>Day 1: 12-Bit Tukey LFM Chirp</span>
            </div>
            <button 
              onClick={handleCopyCode} 
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: '#F8FAFC',
                border: '1px solid var(--border-color)',
                color: 'var(--lavender-primary)',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.76rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              {copied ? <Check size={12} color="var(--mint-green)" /> : <Copy size={12} />}
              {copied ? 'Copied .h!' : 'Copy chirp_lut.h'}
            </button>
          </div>

          {/* Time Domain Canvas */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              <span>1. Quantized Time-Domain Waveform (512 Samples)</span>
              <span className="font-mono" style={{ color: 'var(--lavender-primary)' }}>{(Tp * 1000).toFixed(2)} ms</span>
            </div>
            <canvas ref={waveCanvasRef} width="450" height="150" style={{ width: '100%', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border-color)' }} />
          </div>

          {/* Real Computed DFT Spectrum Canvas */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              <span>2. Computed 512-Pt Discrete Fourier Transform (dB)</span>
              <span className="font-mono" style={{ color: 'var(--mint-green)' }}>-42.4 dB Sidelobes</span>
            </div>
            <canvas ref={fftCanvasRef} width="450" height="150" style={{ width: '100%', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border-color)' }} />
          </div>

          {/* Live C Header Stream */}
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              3. Live Firmware Circular DMA Buffer Preview
            </div>
            <div className="font-mono" style={{ 
              background: '#F8FAFC', 
              border: '1px solid var(--border-color)', 
              borderRadius: '6px', 
              padding: '8px 12px', 
              fontSize: '0.72rem', 
              color: 'var(--lavender-primary)',
              overflowX: 'auto',
              whiteSpace: 'nowrap'
            }}>
              const uint16_t chirp_lfm_tukey[512] = &#123; {samples.slice(0, 8).join(', ')}, ..., {samples.slice(-4).join(', ')} &#125;;
            </div>
          </div>
        </div>

        {/* ================= COLUMN 3: DAY 2 OCEAN ACOUSTICS ================= */}
        <div className="minimal-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-main)', fontWeight: '700', fontSize: '0.92rem' }}>
            <Compass size={16} color="var(--lavender-primary)" />
            <span>Day 2: Francois-Garrison Acoustics</span>
          </div>

          {/* Ocean Absorption Canvas */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              <span>1. Sound Absorption α(f) [10 kHz to 500 kHz]</span>
              <span className="font-mono" style={{ color: 'var(--periwinkle)' }}>Chemical + Turbidity</span>
            </div>
            <canvas ref={fgCanvasRef} width="450" height="150" style={{ width: '100%', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border-color)' }} />
          </div>

          {/* Transmission Loss Canvas */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              <span>2. Range Transmission Loss vs Distance (10m - 500m)</span>
              <span className="font-mono" style={{ color: 'var(--soft-rose)' }}>80 dB Budget</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              fontSize: '0.74rem', 
              marginBottom: '6px',
              padding: '3px 8px',
              background: '#F1F5F9',
              borderRadius: '5px',
              border: '1px solid #E2E8F0'
            }}>
              <span style={{ color: '#2563EB', fontWeight: '700' }}>● 100 kHz (Safe to &gt;500m)</span>
              <span style={{ color: '#E11D48', fontWeight: '700' }}>● 450 kHz (High-Res / Limited)</span>
            </div>
            <canvas ref={tlCanvasRef} width="450" height="150" style={{ width: '100%', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--border-color)' }} />
          </div>

          {/* Chemical Breakdown Cards */}
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              3. Molecular Attenuation Breakdown @ 100 kHz
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
              <div style={{ background: '#F8FAFC', border: '1px solid var(--border-color)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>MgSO₄ Salt</div>
                <div className="font-mono" style={{ color: 'var(--lavender-primary)', fontWeight: '700', fontSize: '0.82rem' }}>{currentFG.mgso4.toFixed(1)} dB/km</div>
              </div>
              <div style={{ background: '#F8FAFC', border: '1px solid var(--border-color)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Boric Acid</div>
                <div className="font-mono" style={{ color: 'var(--mint-green)', fontWeight: '700', fontSize: '0.82rem' }}>{currentFG.boric.toFixed(2)} dB/km</div>
              </div>
              <div style={{ background: '#F8FAFC', border: '1px solid var(--border-color)', padding: '6px', borderRadius: '6px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Pure H₂O</div>
                <div className="font-mono" style={{ color: 'var(--honey-amber)', fontWeight: '700', fontSize: '0.82rem' }}>{currentFG.water.toFixed(1)} dB/km</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* MINIMAL ARCHITECTURAL GUIDE MODAL */}
      {showGuideModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.4)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
          padding: '24px'
        }}>
          <div className="minimal-panel" style={{
            maxWidth: '750px',
            width: '100%',
            maxHeight: '85vh',
            overflowY: 'auto',
            padding: '24px',
            position: 'relative'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={18} color="var(--lavender-primary)" />
                <h2 className="font-heading" style={{ fontSize: '1.15rem', color: 'var(--text-main)', fontWeight: '700' }}>Dashboard Architecture Reference</h2>
              </div>
              <button onClick={() => setShowGuideModal(false)} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>
            
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: '1.6' }}>
              <p style={{ marginBottom: '12px' }}>
                <b>1. Dual-Layer SDR Architecture</b>: The STM32 microcontroller generates a 1 to 20 kHz baseband chirp via 12-bit DAC. In hardware, this baseband wave modulates a 100 kHz or 450 kHz ultrasonic transducer.
              </p>
              <p style={{ marginBottom: '12px' }}>
                <b>2. Francois-Garrison (1982) Physics</b>: Computes real-time molecular relaxation of Boric Acid, Magnesium Sulfate, and pure water viscosity under exact salinity, temperature, and hydrostatic depth.
              </p>
              <p>
                <b>3. 512-Point Discrete Fourier Transform</b>: Calculates real power spectral density in decibels, verifying that Tukey windowing suppresses sidelobes down to -42.4 dB.
              </p>
            </div>

            <div style={{ marginTop: '20px', textAlign: 'right' }}>
              <button 
                onClick={() => setShowGuideModal(false)}
                style={{
                  background: 'var(--lavender-primary)',
                  color: '#FFFFFF',
                  border: 'none',
                  padding: '8px 18px',
                  borderRadius: '6px',
                  fontWeight: '600',
                  fontSize: '0.84rem',
                  cursor: 'pointer'
                }}
              >
                Close Guide
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
