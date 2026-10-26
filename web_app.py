#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_app.py - Interface Web Interativa para Reconstrução 3D por Cruzamento de Retas
Biomecânica - Universidade de São Paulo (USP)
"""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Importar o motor de cálculo do cruzreta.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cruzreta import CruzamentoRetas, Ponto3D, asdict

HTML_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reconstrução 3D por Cruzamento de Retas | Biomecânica USP</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --accent: #10b981;
      --camera1: #3b82f6;
      --camera2: #ef4444;
      --real: #a855f7;
      --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      --mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }

    .container {
      max-width: 1300px;
      margin: 0 auto;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--card-border);
    }

    .header-title h1 {
      font-size: 1.8rem;
      font-weight: 700;
      color: #fff;
    }

    .header-title p {
      color: var(--text-muted);
      font-size: 0.95rem;
    }

    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      background: rgba(56, 189, 248, 0.15);
      color: var(--primary);
      border: 1px solid rgba(56, 189, 248, 0.3);
      margin-bottom: 6px;
    }

    .grid-layout {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 24px;
    }

    @media (max-width: 980px) {
      .grid-layout { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .input-group {
      margin-bottom: 16px;
      padding: 12px;
      border-radius: 8px;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .input-group-label {
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
    }

    .camera-c1-tag { color: var(--camera1); }
    .camera-c2-tag { color: var(--camera2); }
    .real-tag { color: var(--real); }

    .coords-inputs {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
    }

    .coord-field {
      display: flex;
      flex-direction: column;
    }

    .coord-field label {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 2px;
      font-family: var(--mono);
    }

    input[type="number"] {
      width: 100%;
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 6px;
      color: #fff;
      padding: 8px;
      font-family: var(--mono);
      font-size: 0.9rem;
      transition: border-color 0.2s;
    }

    input[type="number"]:focus {
      outline: none;
      border-color: var(--primary);
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
      padding: 10px 16px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }

    .btn-primary {
      background: var(--primary);
      color: #0f172a;
    }
    .btn-primary:hover { background: var(--primary-hover); }

    .btn-secondary {
      background: #334155;
      color: #fff;
      margin-top: 8px;
    }
    .btn-secondary:hover { background: #475569; }

    /* Results stats */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .metric-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 16px;
      text-align: center;
    }

    .metric-card.highlight {
      border-color: var(--accent);
      background: rgba(16, 185, 129, 0.08);
    }

    .metric-title {
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .metric-value {
      font-family: var(--mono);
      font-size: 1.5rem;
      font-weight: 700;
      color: #fff;
    }

    .metric-sub {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* Tables */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }

    th, td {
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }

    th {
      font-size: 0.8rem;
      text-transform: uppercase;
      color: var(--text-muted);
      font-weight: 600;
      background: rgba(15, 23, 42, 0.4);
    }

    td { font-family: var(--mono); }

    .tag-plane {
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.8rem;
    }
    .tag-xy { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .tag-xz { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .tag-zy { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }

    /* Visualizer canvas / SVG */
    .plots-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }

    @media (max-width: 768px) {
      .plots-container { grid-template-columns: 1fr; }
    }

    .plane-canvas-wrap {
      background: #0b1120;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 12px;
      text-align: center;
    }

    .plane-canvas-wrap h4 {
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: var(--text-muted);
    }

    canvas {
      width: 100%;
      height: 220px;
      background: #020617;
      border-radius: 4px;
      display: block;
    }

    .formula-box {
      background: #0b1120;
      padding: 12px;
      border-radius: 8px;
      font-family: var(--mono);
      font-size: 0.85rem;
      color: #38bdf8;
      border-left: 3px solid var(--primary);
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-title">
        <span class="badge">Biomecânica USP • Reconstrução 3D</span>
        <h1>Cruzamento de Retas</h1>
        <p>Interface intuitiva e interativa baseada na planilha original <code>cruzreta.xlsx</code></p>
      </div>
      <div>
        <button class="btn btn-secondary" onclick="restaurarValoresPadrao()" style="width: auto; padding: 8px 14px; font-size: 0.85rem;">
          ↻ Restaurar Padrões da Planilha
        </button>
      </div>
    </header>

    <div class="grid-layout">
      <!-- Painel Esquerdo: Entradas -->
      <div>
        <div class="card">
          <div class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
            Parâmetros de Entrada (3D)
          </div>

          <!-- Câmera 1 -->
          <div class="input-group">
            <div class="input-group-label camera-c1-tag">
              <span>Câmera 1 (Centro Focal C1)</span>
              <span>📷 1</span>
            </div>
            <div class="coords-inputs">
              <div class="coord-field"><label>Xc1</label><input type="number" id="xc1" step="any" value="365.8" oninput="calcular()"></div>
              <div class="coord-field"><label>Yc1</label><input type="number" id="yc1" step="any" value="211.0" oninput="calcular()"></div>
              <div class="coord-field"><label>Zc1</label><input type="number" id="zc1" step="any" value="107.0" oninput="calcular()"></div>
            </div>
          </div>

          <!-- Projeção 1 -->
          <div class="input-group">
            <div class="input-group-label camera-c1-tag">
              <span>Projeção 1 (Ponto Imagem P1)</span>
              <span>🎯 1</span>
            </div>
            <div class="coords-inputs">
              <div class="coord-field"><label>Xp1</label><input type="number" id="xp1" step="any" value="0.0" oninput="calcular()"></div>
              <div class="coord-field"><label>Yp1</label><input type="number" id="yp1" step="any" value="133.9" oninput="calcular()"></div>
              <div class="coord-field"><label>Zp1</label><input type="number" id="zp1" step="any" value="50.9" oninput="calcular()"></div>
            </div>
          </div>

          <!-- Câmera 2 -->
          <div class="input-group">
            <div class="input-group-label camera-c2-tag">
              <span>Câmera 2 (Centro Focal C2)</span>
              <span>📷 2</span>
            </div>
            <div class="coords-inputs">
              <div class="coord-field"><label>Xc2</label><input type="number" id="xc2" step="any" value="131.4" oninput="calcular()"></div>
              <div class="coord-field"><label>Yc2</label><input type="number" id="yc2" step="any" value="384.8" oninput="calcular()"></div>
              <div class="coord-field"><label>Zc2</label><input type="number" id="zc2" step="any" value="151.8" oninput="calcular()"></div>
            </div>
          </div>

          <!-- Projeção 2 -->
          <div class="input-group">
            <div class="input-group-label camera-c2-tag">
              <span>Projeção 2 (Ponto Imagem P2)</span>
              <span>🎯 2</span>
            </div>
            <div class="coords-inputs">
              <div class="coord-field"><label>Xp2</label><input type="number" id="xp2" step="any" value="179.4" oninput="calcular()"></div>
              <div class="coord-field"><label>Yp2</label><input type="number" id="yp2" step="any" value="0.0" oninput="calcular()"></div>
              <div class="coord-field"><label>Zp2</label><input type="number" id="zp2" step="any" value="17.1" oninput="calcular()"></div>
            </div>
          </div>

          <!-- Ponto Real Gabarito -->
          <div class="input-group">
            <div class="input-group-label real-tag">
              <span>Ponto Real Gabarito (Opcional)</span>
              <span>📍 Real</span>
            </div>
            <div class="coords-inputs">
              <div class="coord-field"><label>X real</label><input type="number" id="x_real" step="any" value="159.3" oninput="calcular()"></div>
              <div class="coord-field"><label>Y real</label><input type="number" id="y_real" step="any" value="168.2" oninput="calcular()"></div>
              <div class="coord-field"><label>Z real</label><input type="number" id="z_real" step="any" value="74.9" oninput="calcular()"></div>
            </div>
          </div>

          <button class="btn btn-primary" onclick="calcular()">
            ⚡ Recalcular Agora
          </button>
        </div>
      </div>

      <!-- Painel Direito: Resultados e Gráficos -->
      <div>
        <!-- Cards de Métricas Principais -->
        <div class="metrics-grid">
          <div class="metric-card highlight">
            <div class="metric-title">Coordenada X (REC3D)</div>
            <div class="metric-value" id="val_rec_x">158.6063</div>
            <div class="metric-sub" id="sub_rec_x">Média XY & XZ</div>
          </div>
          <div class="metric-card highlight">
            <div class="metric-title">Coordenada Y (REC3D)</div>
            <div class="metric-value" id="val_rec_y">167.9171</div>
            <div class="metric-sub" id="sub_rec_y">Média XY & ZY</div>
          </div>
          <div class="metric-card highlight">
            <div class="metric-title">Coordenada Z (REC3D)</div>
            <div class="metric-value" id="val_rec_z">75.6636</div>
            <div class="metric-sub" id="sub_rec_z">Média XZ & ZY</div>
          </div>
          <div class="metric-card">
            <div class="metric-title">Erro Médio Total</div>
            <div class="metric-value" id="val_erro_tot" style="color: #38bdf8;">0.5800</div>
            <div class="metric-sub">Planilha cruzreta</div>
          </div>
        </div>

        <!-- Tabela de Detalhamento por Plano -->
        <div class="card">
          <div class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            Cálculos por Plano Ortogonal (Equações de Reta e Cruzamento)
          </div>
          <table>
            <thead>
              <tr>
                <th>Plano</th>
                <th>mr1 (Inclin. 1)</th>
                <th>br1 (Interc. 1)</th>
                <th>mr2 (Inclin. 2)</th>
                <th>br2 (Interc. 2)</th>
                <th>Ponto Interseção (H, V)</th>
              </tr>
            </thead>
            <tbody id="tabela_planos">
              <!-- Preenchido via JavaScript -->
            </tbody>
          </table>

          <div class="formula-box">
            <b>Fórmula de Cruzamento:</b> H = (-(mr2 × ch2) + cv2 + (mr1 × ch1) - cv1) / (mr1 - mr2) | V = mr1 × (H - ch1) + cv1
          </div>
        </div>

        <!-- Tabela de Análise de Erro -->
        <div class="card">
          <div class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            Comparação com Coordenadas Reais (Análise de Erro)
          </div>
          <table>
            <thead>
              <tr>
                <th>Eixo</th>
                <th>REC3D Reconstruído</th>
                <th>Real (Gabarito)</th>
                <th>Erro (Real - Rec)</th>
                <th>Erro Absoluto |Erro|</th>
              </tr>
            </thead>
            <tbody id="tabela_erros">
              <!-- Preenchido via JavaScript -->
            </tbody>
          </table>
          <p style="margin-top: 10px; font-size: 0.85rem; color: var(--text-muted);">
            • <b>Erro Euclidiano 3D (Distância Real - Rec):</b> <span id="val_erro_eucl" style="font-family: var(--mono); color: #fff; font-weight: 600;">1.0697</span>
          </p>
        </div>

        <!-- Gráficos 2D Interativos em Canvas -->
        <div class="card">
          <div class="card-title">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/></svg>
            Visualização Gráfica dos Cruzamentos 2D
          </div>
          <div class="plots-container">
            <div class="plane-canvas-wrap">
              <h4>Plano XY (X horizontal, Y vertical)</h4>
              <canvas id="canvas_xy"></canvas>
            </div>
            <div class="plane-canvas-wrap">
              <h4>Plano XZ (X horizontal, Z vertical)</h4>
              <canvas id="canvas_xz"></canvas>
            </div>
            <div class="plane-canvas-wrap" style="grid-column: 1 / -1;">
              <h4>Plano ZY (Z horizontal, Y vertical)</h4>
              <canvas id="canvas_zy"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    function getVal(id) {
      return parseFloat(document.getElementById(id).value) || 0;
    }

    function restaurarValoresPadrao() {
      document.getElementById('xc1').value = 365.8;
      document.getElementById('yc1').value = 211.0;
      document.getElementById('zc1').value = 107.0;

      document.getElementById('xp1').value = 0.0;
      document.getElementById('yp1').value = 133.9;
      document.getElementById('zp1').value = 50.9;

      document.getElementById('xc2').value = 131.4;
      document.getElementById('yc2').value = 384.8;
      document.getElementById('zc2').value = 151.8;

      document.getElementById('xp2').value = 179.4;
      document.getElementById('yp2').value = 0.0;
      document.getElementById('zp2').value = 17.1;

      document.getElementById('x_real').value = 159.3;
      document.getElementById('y_real').value = 168.2;
      document.getElementById('z_real').value = 74.9;

      calcular();
    }

    function calcPlano(nome, h_label, v_label, ch1, cv1, ph1, pv1, ch2, cv2, ph2, pv2) {
      const mr1 = (pv1 - cv1) / (ph1 - ch1);
      const mr2 = (pv2 - cv2) / (ph2 - ch2);
      const br1 = -1 * (mr1 * ch1 - cv1);
      const br2 = -1 * (mr2 * ch2 - cv2);
      const h = (-(mr2 * ch2) + cv2 + (mr1 * ch1) - cv1) / (mr1 - mr2);
      const v = mr1 * (h - ch1) + cv1;
      return { nome, h_label, v_label, mr1, mr2, br1, br2, h, v };
    }

    function calcular() {
      const c1 = { x: getVal('xc1'), y: getVal('yc1'), z: getVal('zc1') };
      const p1 = { x: getVal('xp1'), y: getVal('yp1'), z: getVal('zp1') };
      const c2 = { x: getVal('xc2'), y: getVal('yc2'), z: getVal('zc2') };
      const p2 = { x: getVal('xp2'), y: getVal('yp2'), z: getVal('zp2') };
      const real = { x: getVal('x_real'), y: getVal('y_real'), z: getVal('z_real') };

      const xy = calcPlano('XY', 'X', 'Y', c1.x, c1.y, p1.x, p1.y, c2.x, c2.y, p2.x, p2.y);
      const xz = calcPlano('XZ', 'X', 'Z', c1.x, c1.z, p1.x, p1.z, c2.x, c2.z, p2.x, p2.z);
      const zy = calcPlano('ZY', 'Z', 'Y', c1.z, c1.y, p1.z, p1.y, c2.z, c2.y, p2.z, p2.y);

      const rec = {
        x: (xy.h + xz.h) / 2,
        y: (xy.v + zy.v) / 2,
        z: (xz.v + zy.h) / 2
      };

      const erro_x = real.x - rec.x;
      const erro_y = real.y - rec.y;
      const erro_z = real.z - rec.z;
      const abs_x = Math.abs(erro_x);
      const abs_y = Math.abs(erro_y);
      const abs_z = Math.abs(erro_z);
      const erro_tot = (abs_x + abs_y + abs_z) / 3;
      const erro_eucl = Math.sqrt(erro_x**2 + erro_y**2 + erro_z**2);

      // Atualizar Cards
      document.getElementById('val_rec_x').innerText = rec.x.toFixed(4);
      document.getElementById('val_rec_y').innerText = rec.y.toFixed(4);
      document.getElementById('val_rec_z').innerText = rec.z.toFixed(4);
      document.getElementById('val_erro_tot').innerText = erro_tot.toFixed(4);
      document.getElementById('val_erro_eucl').innerText = erro_eucl.toFixed(4);

      // Atualizar Tabela de Planos
      const tbodyPlanos = document.getElementById('tabela_planos');
      const tagClass = { 'XY': 'tag-xy', 'XZ': 'tag-xz', 'ZY': 'tag-zy' };
      tbodyPlanos.innerHTML = [xy, xz, zy].map(p => `
        <tr>
          <td><span class="tag-plane ${tagClass[p.nome]}">${p.nome}</span></td>
          <td>${p.mr1.toFixed(6)}</td>
          <td>${p.br1.toFixed(4)}</td>
          <td>${p.mr2.toFixed(6)}</td>
          <td>${p.br2.toFixed(4)}</td>
          <td style="color: #38bdf8; font-weight:600;">${p.h_label}=${p.h.toFixed(4)}, ${p.v_label}=${p.v.toFixed(4)}</td>
        </tr>
      `).join('');

      // Atualizar Tabela de Erros
      const tbodyErros = document.getElementById('tabela_erros');
      tbodyErros.innerHTML = `
        <tr>
          <td><b>X</b></td>
          <td>${rec.x.toFixed(4)}</td>
          <td>${real.x.toFixed(4)}</td>
          <td style="color: ${erro_x >= 0 ? '#34d399' : '#f87171'}">${(erro_x > 0 ? '+' : '') + erro_x.toFixed(4)}</td>
          <td>${abs_x.toFixed(4)}</td>
        </tr>
        <tr>
          <td><b>Y</b></td>
          <td>${rec.y.toFixed(4)}</td>
          <td>${real.y.toFixed(4)}</td>
          <td style="color: ${erro_y >= 0 ? '#34d399' : '#f87171'}">${(erro_y > 0 ? '+' : '') + erro_y.toFixed(4)}</td>
          <td>${abs_y.toFixed(4)}</td>
        </tr>
        <tr>
          <td><b>Z</b></td>
          <td>${rec.z.toFixed(4)}</td>
          <td>${real.z.toFixed(4)}</td>
          <td style="color: ${erro_z >= 0 ? '#34d399' : '#f87171'}">${(erro_z > 0 ? '+' : '') + erro_z.toFixed(4)}</td>
          <td>${abs_z.toFixed(4)}</td>
        </tr>
      `;

      // Desenhar nos canvases
      drawCanvas('canvas_xy', xy, c1.x, c1.y, p1.x, p1.y, c2.x, c2.y, p2.x, p2.y, real.x, real.y);
      drawCanvas('canvas_xz', xz, c1.x, c1.z, p1.x, p1.z, c2.x, c2.z, p2.x, p2.z, real.x, real.z);
      drawCanvas('canvas_zy', zy, c1.z, c1.y, p1.z, p1.y, c2.z, c2.y, p2.z, p2.y, real.z, real.y);
    }

    function drawCanvas(id, plano, c1_h, c1_v, p1_h, p1_v, c2_h, c2_v, p2_h, p2_v, real_h, real_v) {
      const canvas = document.getElementById(id);
      const ctx = canvas.getContext('2d');
      const w = canvas.width = canvas.clientWidth * window.devicePixelRatio || 500;
      const h = canvas.height = canvas.clientHeight * window.devicePixelRatio || 250;

      ctx.clearRect(0, 0, w, h);

      // Determinar limites
      const all_h = [c1_h, p1_h, c2_h, p2_h, plano.h, real_h];
      const all_v = [c1_v, p1_v, c2_v, p2_v, plano.v, real_v];

      let min_h = Math.min(...all_h) - 30;
      let max_h = Math.max(...all_h) + 30;
      let min_v = Math.min(...all_v) - 30;
      let max_v = Math.max(...all_v) + 30;

      const pad = 40;
      function toScreenX(x) {
        return pad + ((x - min_h) / (max_h - min_h)) * (w - 2 * pad);
      }
      function toScreenY(y) {
        return (h - pad) - ((y - min_v) / (max_v - min_v)) * (h - 2 * pad);
      }

      // Grade suave
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      for (let i = 0; i < 5; i++) {
        let gx = pad + (i / 4) * (w - 2 * pad);
        ctx.beginPath(); ctx.moveTo(gx, pad); ctx.lineTo(gx, h - pad); ctx.stroke();
        let gy = pad + (i / 4) * (h - 2 * pad);
        ctx.beginPath(); ctx.moveTo(pad, gy); ctx.lineTo(w - pad, gy); ctx.stroke();
      }

      // Retas das câmeras
      ctx.setLineDash([4, 4]);
      // Reta 1 (Azul)
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(toScreenX(min_h), toScreenY(plano.mr1 * min_h + plano.br1));
      ctx.lineTo(toScreenX(max_h), toScreenY(plano.mr1 * max_h + plano.br1));
      ctx.stroke();

      // Reta 2 (Vermelha)
      ctx.strokeStyle = '#ef4444';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(toScreenX(min_h), toScreenY(plano.mr2 * min_h + plano.br2));
      ctx.lineTo(toScreenX(max_h), toScreenY(plano.mr2 * max_h + plano.br2));
      ctx.stroke();
      ctx.setLineDash([]);

      // Pontos das Câmeras e Projeções
      function drawDot(x, y, color, label, radius=5) {
        const sx = toScreenX(x);
        const sy = toScreenY(y);
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(sx, sy, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px JetBrains Mono';
        ctx.fillText(label, sx + 7, sy - 4);
      }

      drawDot(c1_h, c1_v, '#3b82f6', 'C1', 6);
      drawDot(p1_h, p1_v, '#60a5fa', 'P1', 4);
      drawDot(c2_h, c2_v, '#ef4444', 'C2', 6);
      drawDot(p2_h, p2_v, '#f87171', 'P2', 4);

      // Ponto de Interseção
      drawDot(plano.h, plano.v, '#10b981', 'Cruzamento', 7);

      // Ponto Real Gabarito
      drawDot(real_h, real_v, '#a855f7', 'Real', 6);
    }

    // Inicializar na carga da página
    window.onload = calcular;
  </script>
</body>
</html>
"""


class CruzretaHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silenciar logs verbosos no terminal
        pass


def run_web_server(port: int = 8080, open_browser: bool = True):
    server = HTTPServer(("127.0.0.1", port), CruzretaHTTPHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\n Interface Web iniciada com sucesso!")
    print(f" Acesse em seu navegador: {url}")
    print(" Pressione Ctrl+C para encerrar o servidor.\n")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n Servidor web encerrado.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Servidor Web Interativo para cruzreta")
    parser.add_argument("--port", type=int, default=8080, help="Porta HTTP (padrão: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Não abre navegador automaticamente")
    args = parser.parse_args()
    run_web_server(port=args.port, open_browser=not args.no_browser)
