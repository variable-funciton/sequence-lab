/* アニメーションの共通部品（キャンバス・再生ボタン・グラフ） */
var AN = (function () {
  "use strict";
  var FONT = "13px 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif";

  /** 要素の幅に合わせた高解像度キャンバス。draw(ctx, w, h) を呼ぶ関数を返す */
  function canvas(id, draw) {
    var c = document.getElementById(id), ctx = c.getContext("2d");
    function redraw() {
      var dpr = window.devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
      if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.font = FONT;
      draw(ctx, w, h);
    }
    window.addEventListener("resize", redraw);
    return redraw;
  }

  /** 再生・一時停止。step(dt) が false を返すと止まる */
  function Player(btn, step, labels) {
    labels = labels || ["▶ 再生", "⏸ 一時停止"];
    var running = false, last = 0, self = this;
    function frame(ts) {
      if (!running) return;
      var dt = last ? Math.min(0.05, (ts - last) / 1000) : 0;
      last = ts;
      if (step(dt) === false) { self.stop(); return; }
      requestAnimationFrame(frame);
    }
    this.start = function () { if (running) return; running = true; last = 0; btn.textContent = labels[1]; requestAnimationFrame(frame); };
    this.stop = function () { running = false; btn.textContent = labels[0]; };
    this.running = function () { return running; };
    btn.textContent = labels[0];
    btn.addEventListener("click", function () { if (running) self.stop(); else self.start(); });
  }

  /** グラフの枠。box = {x, y, w, h}（キャンバス上）、xr = [x0, x1]、yr = [y0, y1]。座標変換を返す */
  function axes(ctx, box, xr, yr, opt) {
    opt = opt || {};
    var X = function (x) { return box.x + (x - xr[0]) / (xr[1] - xr[0]) * box.w; };
    var Y = function (y) { return box.y + box.h - (y - yr[0]) / (yr[1] - yr[0]) * box.h; };
    ctx.save();
    ctx.strokeStyle = "#ddd"; ctx.lineWidth = 1; ctx.fillStyle = "#666"; ctx.font = "11px sans-serif";
    (opt.xticks || []).forEach(function (t) { ctx.beginPath(); ctx.moveTo(X(t), box.y); ctx.lineTo(X(t), box.y + box.h); ctx.stroke(); ctx.textAlign = "center"; ctx.fillText(fmt(t), X(t), box.y + box.h + 13); });
    (opt.yticks || []).forEach(function (t) { ctx.beginPath(); ctx.moveTo(box.x, Y(t)); ctx.lineTo(box.x + box.w, Y(t)); ctx.stroke(); ctx.textAlign = "right"; ctx.fillText(fmt(t), box.x - 4, Y(t) + 4); });
    ctx.strokeStyle = "#333"; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(box.x, box.y); ctx.lineTo(box.x, box.y + box.h); ctx.lineTo(box.x + box.w, box.y + box.h); ctx.stroke();
    if (yr[0] < 0 && yr[1] > 0) { ctx.beginPath(); ctx.moveTo(box.x, Y(0)); ctx.lineTo(box.x + box.w, Y(0)); ctx.stroke(); }
    ctx.fillStyle = "#333"; ctx.font = "12px sans-serif";
    if (opt.xlabel) { ctx.textAlign = "right"; ctx.fillText(opt.xlabel, box.x + box.w, box.y + box.h + 28); }
    if (opt.ylabel) { ctx.textAlign = "left"; ctx.fillText(opt.ylabel, box.x + 4, box.y - 6); }
    ctx.restore();
    return { X: X, Y: Y };
  }

  /** 折れ線 */
  function polyline(ctx, M, xs, ys, color, width, dash) {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = width || 2; ctx.setLineDash(dash || []);
    ctx.beginPath();
    var started = false;
    for (var i = 0; i < xs.length; i++) {
      if (ys[i] === null || !isFinite(ys[i])) { started = false; continue; }
      if (!started) { ctx.moveTo(M.X(xs[i]), M.Y(ys[i])); started = true; } else ctx.lineTo(M.X(xs[i]), M.Y(ys[i]));
    }
    ctx.stroke(); ctx.restore();
  }

  function dot(ctx, x, y, r, color) { ctx.save(); ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fill(); ctx.restore(); }

  function text(ctx, s, x, y, color, align, font) {
    ctx.save(); ctx.fillStyle = color || "#333"; ctx.textAlign = align || "left"; if (font) ctx.font = font; ctx.fillText(s, x, y); ctx.restore();
  }

  /** 目盛（だいたい n 本） */
  function ticks(a, b, n) {
    var span = b - a, raw = span / (n || 5), p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    var step = (m < 1.5 ? 1 : m < 3 ? 2 : m < 7 ? 5 : 10) * p, out = [];
    for (var t = Math.ceil(a / step - 1e-9) * step; t <= b + 1e-9; t += step) out.push(Math.round(t / step) * step);
    return out;
  }

  function fmt(v) { var s = Math.abs(v) >= 1000 ? v.toFixed(0) : String(Math.round(v * 1000) / 1000); return s.replace("-", "−"); }

  /** 速さボタン（.speed button[data-v]）。選んだ倍率を返す関数 */
  function speed(container, init) {
    var v = init;
    var bs = container.querySelectorAll("button[data-v]");
    function sync() { bs.forEach(function (b) { b.classList.toggle("on", Number(b.dataset.v) === v); }); }
    bs.forEach(function (b) { b.addEventListener("click", function () { v = Number(b.dataset.v); sync(); }); });
    sync();
    return function () { return v; };
  }

  return { canvas: canvas, Player: Player, axes: axes, polyline: polyline, dot: dot, text: text, ticks: ticks, fmt: fmt, speed: speed };
})();
