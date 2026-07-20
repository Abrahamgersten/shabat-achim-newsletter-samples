(function () {
  "use strict";

  /* ===================== selection state ===================== */
  var GROUP_LABELS = {
    format: "פורמט",
    style: "עיצוב",
    section: "מדור אהוב",
    sharing: "דוגמת שיתוף תוכן",
    levels: "שכבת גיל",
    colorbw: "קובץ",
    fullexample: "דוגמה מלאה"
  };

  var selections = {}; // key: group__id -> { group, id, label }

  function setLikeVisual(btn, selected) {
    btn.setAttribute("aria-pressed", selected ? "true" : "false");
    var heart = btn.querySelector(".heart");
    if (heart) heart.textContent = selected ? "❤️" : "🤍";
  }

  function cardLabel(card) {
    var h4 = card.querySelector("h4");
    if (h4) return h4.textContent.trim();
    var img = card.querySelector("img");
    return img ? img.alt : card.getAttribute("data-id");
  }

  function selectionKey(group, id) { return group + "__" + id; }

  function setSelected(group, id, label, selected) {
    var key = selectionKey(group, id);
    if (selected) {
      selections[key] = { group: group, id: id, label: label };
    } else {
      delete selections[key];
    }
    syncLikeButtons(group, id, selected);
    renderSelectionsUI();
  }

  function isSelected(group, id) {
    return !!selections[selectionKey(group, id)];
  }

  function syncLikeButtons(group, id, selected) {
    var cards = document.querySelectorAll('[data-group="' + group + '"] [data-id="' + cssEscape(id) + '"], .ex-card[data-id="' + cssEscape(id) + '"], .sec-card[data-id="' + cssEscape(id) + '"]');
    // also directly match the figure with this id inside the right group container
    var container = document.querySelector('[data-group="' + group + '"]');
    if (container) {
      var fig = container.querySelector('[data-id="' + cssEscape(id) + '"]');
      if (fig) {
        var btn = fig.querySelector("[data-like]");
        if (btn) setLikeVisual(btn, selected);
      }
    }
    // lightbox like button, if currently showing this item
    var lb = document.getElementById("lightbox");
    if (lb && lb.dataset.group === group && lb.dataset.id === id) {
      var lbLike = document.getElementById("lightboxLike");
      setLikeVisual(lbLike, selected);
    }
  }

  function cssEscape(str) {
    if (window.CSS && CSS.escape) return CSS.escape(str);
    return String(str).replace(/[^a-zA-Z0-9_֐-׿-]/g, "\\$&");
  }

  function renderSelectionsUI() {
    var keys = Object.keys(selections);
    var count = keys.length;

    var bar = document.getElementById("floatingBar");
    var barText = document.getElementById("floatingBarText");
    if (count > 0) {
      bar.hidden = false;
      barText.textContent = count === 1 ? "בחירה 1 נשמרה" : count + " בחירות נשמרו";
    } else {
      bar.hidden = true;
    }

    var panel = document.getElementById("selectionsPanel");
    var list = document.getElementById("selectionsList");
    if (count > 0) {
      panel.hidden = false;
      list.innerHTML = "";
      keys.forEach(function (k) {
        var sel = selections[k];
        var li = document.createElement("li");
        li.textContent = (GROUP_LABELS[sel.group] || sel.group) + ": " + sel.label;
        list.appendChild(li);
      });
    } else {
      panel.hidden = true;
    }

    syncDesignField();
  }

  var designFieldDirty = false;

  function buildDesignSummary() {
    var byGroup = {};
    Object.keys(selections).forEach(function (k) {
      var sel = selections[k];
      byGroup[sel.group] = byGroup[sel.group] || [];
      byGroup[sel.group].push(sel.label);
    });
    var parts = [];
    Object.keys(byGroup).forEach(function (g) {
      parts.push((GROUP_LABELS[g] || g) + ": " + byGroup[g].join(", "));
    });
    return parts.join(" | ");
  }

  function syncDesignField() {
    if (designFieldDirty) return;
    var field = document.getElementById("f_design");
    if (!field) return;
    field.value = buildDesignSummary();
  }

  /* ===================== like buttons (delegated) ===================== */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-like]");
    if (!btn) return;
    var card = btn.closest("[data-id]");
    if (!card) return;
    var groupContainer = btn.closest("[data-group]");
    var group = groupContainer ? groupContainer.getAttribute("data-group") : "other";
    var id = card.getAttribute("data-id");
    var label = cardLabel(card);
    var nowSelected = btn.getAttribute("aria-pressed") !== "true";
    setLikeVisual(btn, nowSelected);
    setSelected(group, id, label, nowSelected);
  });

  /* ===================== lightbox ===================== */
  var lightbox = document.getElementById("lightbox");
  var lightboxImg = document.getElementById("lightboxImg");
  var lightboxClose = document.getElementById("lightboxClose");
  var lightboxLike = document.getElementById("lightboxLike");
  var lightboxPdf = document.getElementById("lightboxPdf");
  var lastFocused = null;

  function openLightbox(card) {
    var full = card.getAttribute("data-full");
    var pdf = card.getAttribute("data-pdf");
    var group = card.closest("[data-group]");
    group = group ? group.getAttribute("data-group") : "other";
    var id = card.getAttribute("data-id");
    var label = cardLabel(card);
    var img = card.querySelector("img");

    lightboxImg.src = full || (img ? img.src : "");
    lightboxImg.alt = img ? img.alt : label;
    lightbox.dataset.group = group;
    lightbox.dataset.id = id;
    setLikeVisual(lightboxLike, isSelected(group, id));

    if (pdf) {
      lightboxPdf.href = pdf;
      lightboxPdf.hidden = false;
    } else {
      lightboxPdf.hidden = true;
    }

    lastFocused = document.activeElement;
    lightbox.hidden = false;
    document.body.style.overflow = "hidden";
    lightboxClose.focus();
  }

  function closeLightbox() {
    lightbox.hidden = true;
    document.body.style.overflow = "";
    if (lastFocused) lastFocused.focus();
  }

  document.addEventListener("click", function (e) {
    var zoomBtn = e.target.closest(".ex-zoom");
    if (!zoomBtn) return;
    var card = zoomBtn.closest("[data-id]");
    if (card) openLightbox(card);
  });

  lightboxClose.addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", function (e) {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !lightbox.hidden) closeLightbox();
  });
  lightboxLike.addEventListener("click", function () {
    var group = lightbox.dataset.group;
    var id = lightbox.dataset.id;
    var nowSelected = lightboxLike.getAttribute("aria-pressed") !== "true";
    setLikeVisual(lightboxLike, nowSelected);
    var card = document.querySelector('[data-group="' + group + '"] [data-id="' + cssEscape(id) + '"]');
    var label = card ? cardLabel(card) : id;
    setSelected(group, id, label, nowSelected);
  });

  /* ===================== signup form ===================== */
  var FORM_ACTION = "https://docs.google.com/forms/d/e/1FAIpQLSfpy_D43zcI6u_nmFB6nJ34jB9s2x50vXuO0VouViJmVQgwuQ/formResponse";
  var ENTRY = {
    name: "entry.767854375",
    school: "entry.1930497489",
    role: "entry.1422445692",
    phone: "entry.1827662671",
    design: "entry.845003439",
    message: "entry.1049837068"
  };

  var designField = document.getElementById("f_design");
  if (designField) {
    designField.addEventListener("input", function () { designFieldDirty = true; });
  }

  var undecided = document.getElementById("f_undecided");
  if (undecided) {
    undecided.addEventListener("change", function () {
      if (undecided.checked) {
        designFieldDirty = true;
        designField.value = "עדיין לא בחרתי - אשמח שתעזרו לי לבחור בשיחה אישית";
      } else {
        designFieldDirty = false;
        syncDesignField();
      }
    });
  }

  var form = document.getElementById("signupForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var errorEl = document.getElementById("formError");
      var successEl = document.getElementById("formSuccess");
      errorEl.hidden = true;

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      var submitBtn = form.querySelector(".btn-submit");
      submitBtn.disabled = true;
      submitBtn.textContent = "שולח...";

      var fd = new FormData();
      fd.append(ENTRY.name, form.name.value.trim());
      fd.append(ENTRY.school, form.school.value.trim());
      fd.append(ENTRY.role, form.role.value.trim());
      fd.append(ENTRY.phone, form.phone.value.trim());
      fd.append(ENTRY.design, form.design.value.trim());
      fd.append(ENTRY.message, form.message.value.trim());

      fetch(FORM_ACTION, { method: "POST", mode: "no-cors", body: fd })
        .then(function () {
          onSubmitDone(true);
        })
        .catch(function () {
          onSubmitDone(false);
        });

      function onSubmitDone(ok) {
        submitBtn.disabled = false;
        submitBtn.textContent = "שליחת הבחירות והצטרפות לחודש חינם";
        if (ok) {
          form.hidden = true;
          successEl.hidden = false;
          successEl.scrollIntoView({ behavior: "smooth", block: "center" });
        } else {
          errorEl.hidden = false;
        }
      }
    });
  }

  /* init */
  renderSelectionsUI();
})();
