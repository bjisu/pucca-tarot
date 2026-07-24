/* ═══════════════════════════════════════════════════════════
   뿌까 오라클 — 프론트엔드 SPA (해시 라우팅)
   흐름: 홈 → 질문 선택 → 카드 뽑기(스와이프) → 결과
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  const $app = document.getElementById("app");
  const $overlay = document.getElementById("overlay");
  const $overlayText = document.getElementById("overlay-text");

  // 에셋 캐시 무효화 버전 — 같은 파일명으로 이미지를 교체하면 이 값을 올려주세요.
  const ASSET_VER = "20260724-3";

  /* ── 상태 (새로고침 대비 sessionStorage 유지) ── */
  const STORE_KEY = "pucca_state_v1";
  let state = loadState() || {
    mode: null,          // 'today' | 'classic'
    question: "",
    catIndex: 0,
    reading: null,       // 리딩 결과 전체
    dexTab: 0,
  };
  let DATA = { cards: null, categories: null };

  function loadState() {
    try { return JSON.parse(sessionStorage.getItem(STORE_KEY)); }
    catch (e) { return null; }
  }
  function saveState() {
    try { sessionStorage.setItem(STORE_KEY, JSON.stringify(state)); }
    catch (e) { /* ignore */ }
  }

  /* ── 유틸 ── */
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function getUuid() {
    const p = new URLSearchParams(location.search).get("uuid");
    if (p) return p;
    let u = localStorage.getItem("pucca_uuid");
    if (!u) {
      u = "anon-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      localStorage.setItem("pucca_uuid", u);
    }
    return u;
  }
  function showOverlay(text) {
    $overlayText.textContent = text || "카드를 읽고 있어...";
    $overlay.classList.remove("hidden");
  }
  function hideOverlay() { $overlay.classList.add("hidden"); }

  async function api(path, opts) {
    const res = await fetch(path, opts);
    if (!res.ok) throw new Error("api " + res.status);
    return res.json();
  }
  function post(path, body) {
    return api(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  }

  /* ── 공용 컴포넌트 HTML ── */
  function puccaHTML(cls) {
    return '<div class="pucca ' + (cls || "") + '">' +
      '<span class="pucca-fb">뿌까</span>' +
      '<img src="/assets/character/pucca_main.png" alt="" onerror="this.remove()">' +
      "</div>";
  }
  function cardBackHTML() {
    // 카드 뒷면: assets/image/card.webp가 있으면 이미지, 없으면 CSS 오너먼트 폴백
    return '<div class="card-back">' +
      '<img src="/assets/image/card.webp?v=' + ASSET_VER + '" alt="" onerror="this.remove()">' +
      "</div>";
  }
  function cardFaceHTML(card) {
    return '<div class="card-face">' +
      '<div class="card-ph">' +
      '<div class="card-ph-star">✦</div>' +
      '<div class="card-ph-name">' + esc(card.name_en) + "</div>" +
      "</div>" +
      '<img src="/assets/' + esc(card.image) + "?v=" + ASSET_VER + '" alt="' + esc(card.name_en) + '" loading="lazy" decoding="async" onerror="this.remove()">' +
      "</div>";
  }

  /* ═══════════ 라우터 ═══════════ */
  function route() {
    const hash = location.hash || "#/";
    window.scrollTo(0, 0);
    if (hash === "#/" || hash === "") return renderHome();
    if (hash === "#/question") {
      if (!state.mode) return go("#/");
      return renderQuestion();
    }
    if (hash === "#/draw") {
      if (!state.mode || !state.question) return go("#/");
      return renderDraw();
    }
    if (hash === "#/result") {
      if (!state.reading) return go("#/");
      return renderResult();
    }
    if (hash === "#/dex") return renderDex();
    if (hash.indexOf("#/dex/") === 0) {
      const id = parseInt(hash.slice(6), 10);
      return renderDexDetail(id);
    }
    return renderHome();
  }
  function go(hash) {
    if (location.hash === hash) route();
    else location.hash = hash;
  }
  window.addEventListener("hashchange", route);

  /* ═══════════ 홈 ═══════════ */
  function renderHome() {
    $app.innerHTML =
      '<section class="screen home-screen">' +
      menuCard("Classic Tarot", "클래식 타로", "카드 3장으로 구체적으로 운명을 점쳐줄게", "classic", "content_1.webp") +
      menuCard("Today's Tarot", "오늘의 타로", "오늘의 운세를 카드 1장으로 간편하게 점쳐줄게", "today", "content_2.webp") +
      menuCard("Tarot Card List", "타로 카드 도감", "타로를 알고 보면 더 재밌어!", "dex", "content_3.webp") +
      "</section>";

    $app.querySelectorAll("[data-menu]").forEach(function (el) {
      el.addEventListener("click", function () {
        const m = el.getAttribute("data-menu");
        if (m === "dex") { go("#/dex"); return; }
        state.mode = m;
        state.question = "";
        saveState();
        go("#/question");
      });
    });

    function menuCard(badge, title, desc, key, img) {
      return '<button class="menu-card" data-menu="' + key + '">' +
        '<span class="menu-hero">' +
        '<span class="menu-badge">' + badge + "</span>" +
        '<img class="menu-img" src="/assets/image/' + img + "?v=" + ASSET_VER + '" alt="" onerror="this.remove()">' +
        "</span>" +
        '<span class="menu-foot"><h2>' + title + "</h2><p>" + desc + "</p></span>" +
        "</button>";
    }
  }

  /* ═══════════ 질문 선택 ═══════════ */
  function renderQuestion() {
    const cats = DATA.categories.categories;
    if (state.catIndex >= cats.length) state.catIndex = 0;

    $app.innerHTML =
      '<section class="screen">' +
      '<div class="q-hero">' +
      '<div class="q-hero-text">' +
      '<span class="l1">요즘 어떤 고민이 있어?</span>' +
      '<span class="l2">고민을 알려줘!</span>' +
      "</div>" +
      '<img class="q-hero-pucca" src="/assets/image/hero.png?v=' + ASSET_VER + '" alt="뿌까" onerror="this.remove()">' +
      "</div>" +
      '<input id="qInput" class="q-input" type="text" maxlength="120" ' +
      'placeholder="고민을 선택하거나 직접 입력해봐!" value="' + esc(state.question) + '">' +
      '<nav class="cat-tabs" id="catTabs"></nav>' +
      '<div class="q-list" id="qList"></div>' +
      '<div class="q-submit-wrap"><button id="qGo" class="btn btn-gold">이 고민으로 카드 뽑으러 가기</button></div>' +
      "</section>";

    const $input = document.getElementById("qInput");
    const $tabs = document.getElementById("catTabs");
    const $list = document.getElementById("qList");

    function renderTabs() {
      $tabs.innerHTML = cats.map(function (c, i) {
        return '<button class="cat-tab' + (i === state.catIndex ? " active" : "") + '" data-i="' + i + '">' +
          c.emoji + " " + esc(c.name) + "</button>";
      }).join("");
      $tabs.querySelectorAll(".cat-tab").forEach(function (b) {
        b.addEventListener("click", function () {
          state.catIndex = parseInt(b.getAttribute("data-i"), 10);
          saveState();
          renderTabs(); renderList();
          b.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
        });
      });
    }
    function renderList() {
      // 질문 앞 이모지는 표시하지 않는다 (데이터의 emoji 필드는 무시)
      $list.innerHTML = cats[state.catIndex].questions.map(function (q) {
        return '<button class="q-item" data-q="' + esc(q.text) + '">' +
          "<span>" + esc(q.text) + "</span></button>";
      }).join("");
      $list.querySelectorAll(".q-item").forEach(function (b) {
        b.addEventListener("click", function () {
          $input.value = b.getAttribute("data-q");
          state.question = $input.value;
          saveState();
        });
      });
    }
    renderTabs(); renderList();

    $input.addEventListener("input", function () {
      state.question = $input.value; saveState();
    });
    document.getElementById("qGo").addEventListener("click", function () {
      const q = $input.value.trim();
      if (!q) {
        $input.focus();
        $input.placeholder = "고민을 하나 골라주면 카드를 봐줄게!";
        return;
      }
      state.question = q;
      state.reading = null;
      saveState();
      go("#/draw");
    });
  }

  /* ═══════════ 카드 뽑기 (스와이프 덱) ═══════════ */
  function renderDraw() {
    const needed = state.mode === "today" ? 1 : 3;
    let picked = 0;
    let picking = false;

    $app.innerHTML =
      '<section class="screen draw-screen">' +
      '<div class="q-hero">' +
      '<div class="q-hero-text">' +
      '<span class="l1">고민을 생각하면서</span>' +
      '<span class="l2">카드 ' + needed + '장을 뽑아봐!</span>' +
      "</div>" +
      '<img class="q-hero-pucca" src="/assets/image/hero2.png?v=' + ASSET_VER + '" alt="뿌까" onerror="this.remove()">' +
      "</div>" +
      '<div class="slots" id="slots">' +
      Array.from({ length: needed }).map(function () {
        return '<div class="slot">미선택</div>';
      }).join("") +
      "</div>" +
      '<div class="deck-area" id="deckArea"></div>' +
      '<p class="deck-hint">카드를 좌우로 이동해 보세요</p>' +
      "</section>";

    const $slots = Array.prototype.slice.call(document.querySelectorAll("#slots .slot"));
    const $area = document.getElementById("deckArea");

    /* ── 부채꼴 덱 ── */
    const COUNT = 30;
    const els = [];
    let center = Math.floor(COUNT / 2); // 정수로 시작해야 중앙 강조 카드가 항상 존재한다
    for (let i = 0; i < COUNT; i++) {
      const el = document.createElement("div");
      el.className = "deck-card";
      el.innerHTML = cardBackHTML();
      $area.appendChild(el);
      els.push(el);
    }
    function clampCenter(v) {
      return Math.min(Math.max(v, 0), els.length - 1);
    }
    /* 거대한 원(회전축 카드 위 560px 아래)의 윗부분 호를 따라 촘촘히 배치.
       카드당 3.8° → 이웃 간격 약 37px(카드폭 96px과 겹침), 뷰포트 390px에 13장 안팎.
       호 배치는 rotate만 담당 — 중앙 카드 떠오름·확대·글로우는 CSS(.centered .card-back)가 처리.
       뷰포트 밖(중앙에서 8.5장 초과)은 opacity로 정리 — 화면 안 카드는 절대 페이드되지 않음 */
    const STEP_DEG = 3.8;
    const STEP_PX = 560 * Math.sin(STEP_DEG * Math.PI / 180); // 이웃 카드 가로 간격 ≈ 31px
    function layout(snap) {
      els.forEach(function (el, i) {
        const off = i - center;
        const a = Math.abs(off);
        el.classList.toggle("snap", !!snap);
        el.classList.toggle("centered", a < 0.5);
        el.style.zIndex = String(200 - Math.round(a * 10));
        el.style.opacity = a > 8.5 ? "0" : "1";
        el.style.pointerEvents = a > 8.5 ? "none" : "";
        el.style.transform = "rotate(" + (off * STEP_DEG) + "deg)";
      });
    }
    layout(true);

    /* 드래그 / 스와이프 */
    let dragging = false, startX = 0, startCenter = 0, moved = 0, tapTarget = null;
    $area.addEventListener("pointerdown", function (e) {
      if (picking) return;
      dragging = true; startX = e.clientX; startCenter = center; moved = 0;
      // setPointerCapture 이후에는 e.target이 컨테이너로 바뀌므로 지금 기억해둔다
      tapTarget = e.target.closest ? e.target.closest(".deck-card") : null;
      $area.setPointerCapture(e.pointerId);
    });
    $area.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      const dx = e.clientX - startX;
      moved = Math.max(moved, Math.abs(dx));
      if (moved > 6) {
        // 카드 간격이 좁아 1:1이면 너무 빨리 넘어감 — 손가락 이동의 절반 속도로
        center = clampCenter(startCenter - dx / (STEP_PX * 2));
        layout(false);
      }
    });
    $area.addEventListener("pointerup", function () {
      if (!dragging) return;
      dragging = false;
      if (moved < 8 && tapTarget && tapTarget.isConnected) {
        const idx = els.indexOf(tapTarget);
        if (idx !== -1) {
          if (idx === Math.round(center)) { pick(tapTarget); tapTarget = null; return; }
          center = clampCenter(idx); layout(true); tapTarget = null; return;
        }
      }
      tapTarget = null;
      center = clampCenter(Math.round(center));
      layout(true);
    });
    $area.addEventListener("pointercancel", function () {
      dragging = false; center = clampCenter(Math.round(center)); layout(true);
    });

    /* 카드 선택 → 슬롯으로 날아가는 연출 */
    function pick(el) {
      if (picking || picked >= needed) return;
      picking = true;
      const slot = $slots[picked];
      const back = el.querySelector(".card-back");
      const from = back.getBoundingClientRect();

      const fly = document.createElement("div");
      fly.className = "fly-card";
      fly.innerHTML = cardBackHTML();
      fly.style.left = from.left + "px";
      fly.style.top = from.top + "px";
      fly.style.width = from.width + "px";
      fly.style.height = from.height + "px";
      document.body.appendChild(fly);

      const idx = els.indexOf(el);
      els.splice(idx, 1);
      el.remove();
      center = clampCenter(idx);
      layout(true);

      const to = slot.getBoundingClientRect();
      requestAnimationFrame(function () {
        fly.style.left = to.left + "px";
        fly.style.top = to.top + "px";
        fly.style.width = to.width + "px";
        fly.style.height = to.height + "px";
      });
      setTimeout(function () {
        fly.remove();
        slot.classList.add("filled");
        slot.innerHTML = cardBackHTML();
        picked++;
        picking = false;
        if (picked >= needed) setTimeout(submitReading, 450);
      }, 580);
    }

    /* 서버에 리딩 요청 — 응답이 빨라도 로딩 화면을 최소 2초는 보여준다 */
    function submitReading() {
      showOverlay("뿌까가 카드를 읽고 있어...");
      const startedAt = Date.now();
      const MIN_LOADING_MS = 2000;
      function afterMinLoading(fn) {
        setTimeout(fn, Math.max(0, MIN_LOADING_MS - (Date.now() - startedAt)));
      }
      const path = state.mode === "today" ? "/api/reading/today" : "/api/reading/classic";
      post(path, { uuid: getUuid(), question: state.question })
        .then(function (data) {
          afterMinLoading(function () {
            hideOverlay();
            if (data.crisis) { renderCrisis(data.message); return; }
            state.reading = data;
            saveState();
            go("#/result");
          });
        })
        .catch(function () {
          afterMinLoading(function () {
            hideOverlay();
            $app.innerHTML =
              '<section class="screen"><div class="error-box">' +
              "<p>잠깐 별이 흐려졌어, 다시 해볼래?</p>" +
              '<div class="btn-row">' +
              '<button class="btn btn-ghost" id="errHome">처음으로</button>' +
              '<button class="btn btn-gold" id="errRetry">다시 시도</button>' +
              "</div></div></section>";
            document.getElementById("errRetry").addEventListener("click", submitReading);
            document.getElementById("errHome").addEventListener("click", function () { go("#/"); });
          });
        });
    }
  }

  /* ═══════════ 위기 안내 화면 ═══════════ */
  function renderCrisis(message) {
    $app.innerHTML =
      '<section class="screen">' +
      '<div class="hero">' + puccaHTML("") +
      '<div class="hero-text"><h2>잠깐, 이 얘기 먼저 하자</h2></div></div>' +
      '<div class="crisis-box">' + esc(message) + "</div>" +
      '<button class="btn btn-gold" id="crisisHome">홈으로</button>' +
      "</section>";
    document.getElementById("crisisHome").addEventListener("click", function () { go("#/"); });
  }

  /* ═══════════ 결과 ═══════════ */
  function renderResult() {
    const r = state.reading;
    const isToday = r.reading_type === "today";
    const cards = isToday ? [{ card: r.card, position: null }] :
      r.positions.map(function (p) { return { card: p.card, position: p.position }; });

    let html = '<section class="screen">' +
      '<div class="result-q"><span class="badge">' +
      (isToday ? "Today's Tarot" : "Classic Tarot") + "</span>" + esc(r.question) + "</div>" +
      '<div class="result-cards">' +
      cards.map(function (c, i) {
        return '<div><div class="flip' + (isToday ? " big" : "") + '" id="flip' + i + '">' +
          '<div class="flip-inner">' + cardBackHTML() + cardFaceHTML(c.card) + "</div></div>" +
          (c.position ? '<div class="flip-label">' + esc(c.position) + "</div>" : "") +
          '<div class="flip-name">' + esc(c.card.name_en) + "</div>" +
          "</div>";
      }).join("") +
      "</div>";

    const delayBase = cards.length * 0.7 + 0.6;
    if (isToday) {
      html +=
        wrapFade('<p class="one-line">"' + esc(r.one_line) + '"</p>', delayBase) +
        wrapFade(section("뿌까의 해석", r.interpretation, r.card), delayBase + 0.25) +
        wrapFade(section("오늘의 조언", r.advice), delayBase + 0.5);
    } else {
      html += r.positions.map(function (p, i) {
        return wrapFade(sectionWithCard("① ② ③".split(" ")[i] + " " + p.position, p.interpretation, p.card), delayBase + i * 0.25);
      }).join("") +
        wrapFade(section("종합 해석", r.overall), delayBase + 0.9) +
        wrapFade(section("실천 조언", r.advice), delayBase + 1.1);
    }

    html +=
      '<div class="result-actions result-fade" style="animation-delay:' + (delayBase + 1.3) + 's">' +
      '<button class="btn btn-gold" id="goHome">홈으로</button>' +
      "</div></section>";

    $app.innerHTML = html;

    cards.forEach(function (_, i) {
      setTimeout(function () {
        const f = document.getElementById("flip" + i);
        if (f) f.classList.add("flipped");
      }, 500 + i * 650);
    });

    document.getElementById("goHome").addEventListener("click", function () { go("#/"); });

    function wrapFade(inner, delay) {
      return '<div class="result-fade" style="animation-delay:' + delay + 's">' + inner + "</div>";
    }
    function section(title, body, card) {
      let kws = "";
      if (card) {
        kws = '<div class="keywords">' + card.keywords.map(function (k) {
          return '<span class="kw">#' + esc(k) + "</span>";
        }).join("") + "</div>";
      }
      return '<div class="section"><h3>' + esc(title) + "</h3><p>" + esc(body) + "</p>" + kws + "</div>";
    }
    function sectionWithCard(title, body, card) {
      return '<div class="section"><h3>' + esc(title) + " · " + esc(card.name_en) + "</h3>" +
        '<div class="sec-card">' + cardFaceHTML(card) + "<p>" + esc(body) + "</p></div></div>";
    }
  }

  /* ═══════════ 타로 카드 도감 ═══════════ */
  /* 탭 이모지는 구형 기기 호환을 위해 유니코드 6~8 범위만 사용
     (U+1FA84 마술봉, U+1FA99 동전은 유니코드 13이라 구형 기기에서 네모로 깨짐) */
  const DEX_TABS = [
    { label: "🌟 Major Arcana", filter: function (c) { return c.arcana === "Major Arcana"; } },
    { label: "🔥 Wands", filter: function (c) { return c.suit === "Wands"; } },
    { label: "🍷 Cups", filter: function (c) { return c.suit === "Cups"; } },
    { label: "🗡️ Swords", filter: function (c) { return c.suit === "Swords"; } },
    { label: "💰 Pentacles", filter: function (c) { return c.suit === "Pentacles"; } },
  ];

  function renderDex() {
    if (state.dexTab >= DEX_TABS.length) state.dexTab = 0;
    $app.innerHTML =
      '<section class="screen dex-screen">' +
      '<div class="dex-head">' +
      '<button class="back-chevron" id="dexBack" aria-label="뒤로가기"></button>' +
      "<h2>타로 카드 도감</h2></div>" +
      '<nav class="cat-tabs" id="dexTabs"></nav>' +
      '<div class="dex-grid" id="dexGrid"></div>' +
      "</section>";

    document.getElementById("dexBack").addEventListener("click", function () { go("#/"); });

    const $tabs = document.getElementById("dexTabs");
    const $grid = document.getElementById("dexGrid");

    function renderTabs() {
      $tabs.innerHTML = DEX_TABS.map(function (t, i) {
        return '<button class="cat-tab' + (i === state.dexTab ? " active" : "") + '" data-i="' + i + '">' + t.label + "</button>";
      }).join("");
      $tabs.querySelectorAll(".cat-tab").forEach(function (b) {
        b.addEventListener("click", function () {
          state.dexTab = parseInt(b.getAttribute("data-i"), 10);
          saveState();
          renderTabs(); renderGrid();
        });
      });
    }
    function renderGrid() {
      const list = DATA.cards.cards.filter(DEX_TABS[state.dexTab].filter);
      $grid.innerHTML = list.map(function (c) {
        return '<figure class="dex-item" data-id="' + c.id + '">' + cardFaceHTML(c) +
          "<figcaption>" + esc(c.name_en) + "</figcaption></figure>";
      }).join("");
      $grid.querySelectorAll(".dex-item").forEach(function (f) {
        f.addEventListener("click", function () {
          go("#/dex/" + f.getAttribute("data-id"));
        });
      });
    }
    renderTabs(); renderGrid();
  }

  function renderDexDetail(id) {
    const card = DATA.cards.cards.find(function (c) { return c.id === id; });
    if (!card) return go("#/dex");
    $app.innerHTML =
      '<section class="screen dex-detail">' +
      '<div class="dex-head"><button class="back-chevron" id="detailBack" aria-label="뒤로가기"></button></div>' +
      '<div class="dex-detail-card">' + cardFaceHTML(card) + "</div>" +
      "<h2>" + esc(card.name_en) + "</h2>" +
      '<div class="arcana-tag">' + esc(card.arcana) + (card.suit ? " · " + esc(card.suit) : "") + "</div>" +
      section("카드의 의미", card.meaning) +
      section("한 줄 리딩", card.reading_sentence) +
      '<div class="section"><h3>키워드</h3><div class="keywords">' +
      card.keywords.map(function (k) { return '<span class="kw">#' + esc(k) + "</span>"; }).join("") +
      "</div></div>" +
      "</section>";
    document.getElementById("detailBack").addEventListener("click", function () { go("#/dex"); });

    function section(title, body) {
      return '<div class="section"><h3>' + esc(title) + "</h3><p>" + esc(body) + "</p></div>";
    }
  }

  /* ═══════════ 부트 ═══════════ */
  function boot() {
    showOverlay("별빛을 모으고 있어...");
    Promise.all([api("/api/cards"), api("/api/categories")])
      .then(function (res) {
        hideOverlay();
        DATA.cards = res[0];
        DATA.categories = res[1];
        route();
      })
      .catch(function () {
        hideOverlay();
        $app.innerHTML =
          '<section class="screen"><div class="error-box">' +
          "<p>서버와 연결할 수 없어. 서버가 켜져 있는지 확인해줘!</p>" +
          '<button class="btn btn-gold" id="bootRetry">다시 시도</button></div></section>';
        document.getElementById("bootRetry").addEventListener("click", boot);
      });
  }
  boot();
})();
