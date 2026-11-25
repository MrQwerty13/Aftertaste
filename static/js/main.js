(() => {
  "use strict";

  const body = document.body;
  const csrfToken =
    document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") ||
    getCookie("csrftoken");

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  function loginRedirect() {
    const next = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.href = `/login/?next=${next}`;
  }

  async function postJSON(url) {
    return fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "X-Requested-With": "fetch",
        "X-CSRFToken": csrfToken,
      },
      credentials: "same-origin",
    });
  }

  // Like buttons ----------------------------------------------------------
  const likeText = body.dataset.i18nLike || "Like";
  const likedText = body.dataset.i18nLiked || "Liked";
  const likeError = body.dataset.i18nLikeError || "Could not update like.";

  document.querySelectorAll(".like-btn[data-url]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (button.disabled) return;
      button.disabled = true;
      try {
        const response = await postJSON(button.dataset.url);
        if (response.status === 401) {
          loginRedirect();
          return;
        }
        if (!response.ok) throw new Error("like failed");

        const data = await response.json();
        const label = button.querySelector(".like-label");
        const count = button.querySelector("[data-count]");

        button.dataset.liked = data.liked ? "true" : "false";
        button.classList.toggle("is-liked", data.liked);
        if (label) label.textContent = data.liked ? likedText : likeText;
        if (count) count.textContent = String(data.like_count);

        button.classList.remove("pop");
        void button.offsetWidth;
        button.classList.add("pop");
      } catch (error) {
        console.error(error);
        window.alert(likeError);
      } finally {
        button.disabled = false;
      }
    });
  });

  // Repost buttons --------------------------------------------------------
  const repostText = body.dataset.i18nRepost || "Repost";
  const repostedText = body.dataset.i18nReposted || "Reposted";
  const repostError = body.dataset.i18nRepostError || "Could not update repost.";

  document.querySelectorAll(".repost-btn[data-url]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (button.disabled) return;
      button.disabled = true;
      try {
        const response = await postJSON(button.dataset.url);
        if (response.status === 401) {
          loginRedirect();
          return;
        }
        if (!response.ok) throw new Error("repost failed");

        const data = await response.json();
        const label = button.querySelector(".repost-label");
        const count = button.querySelector("[data-count]");

        button.dataset.reposted = data.reposted ? "true" : "false";
        button.classList.toggle("is-reposted", data.reposted);
        if (label) label.textContent = data.reposted ? repostedText : repostText;
        if (count) count.textContent = String(data.repost_count);

        button.classList.remove("pop");
        void button.offsetWidth;
        button.classList.add("pop");
      } catch (error) {
        console.error(error);
        window.alert(repostError);
      } finally {
        button.disabled = false;
      }
    });
  });

  // Accent slider ---------------------------------------------------------
  const accentSlider = document.getElementById("accent-slider");
  const accentPreview = document.getElementById("accent-preview");
  const accentForm = document.getElementById("accent-form");

  if (accentSlider) {
    const applyHue = (hue) => {
      document.documentElement.style.setProperty("--accent-h", String(hue));
      if (accentPreview) {
        accentPreview.style.background = `hsl(${hue} 70% 48%)`;
      }
    };

    accentSlider.addEventListener("input", () => applyHue(accentSlider.value));
    accentSlider.addEventListener("change", () => {
      if (accentForm) accentForm.requestSubmit();
    });
  }

  // Quick-add form --------------------------------------------------------
  const quickForm = document.getElementById("quick-form");
  const quickStatus = document.getElementById("quick-status");

  if (quickForm) {
    quickForm.querySelectorAll(".quick-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const input = quickForm.querySelector('[name="drink_name"]');
        if (input) {
          input.value = chip.dataset.drink || "";
          input.focus();
        }
      });
    });

    quickForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submit = quickForm.querySelector('button[type="submit"]');
      if (submit) submit.disabled = true;
      try {
        const response = await fetch(quickForm.action, {
          method: "POST",
          headers: {
            Accept: "application/json",
            "X-Requested-With": "fetch",
            "X-CSRFToken": csrfToken,
          },
          body: new FormData(quickForm),
          credentials: "same-origin",
        });

        if (response.status === 401) {
          loginRedirect();
          return;
        }

        const data = await response.json().catch(() => ({}));
        if (response.ok && data.ok) {
          const successMessage = data.message || quickForm.dataset.success;
          if (quickStatus) {
            quickStatus.textContent = successMessage;
            quickStatus.className = "quick-status is-ok";
          }
          quickForm.reset();
          quickForm.querySelector('[name="drink_name"]')?.focus();
        } else {
          if (quickStatus) {
            quickStatus.textContent = quickForm.dataset.error;
            quickStatus.className = "quick-status is-error";
          }
        }
      } catch (error) {
        console.error(error);
        if (quickStatus) {
          quickStatus.textContent = quickForm.dataset.error;
          quickStatus.className = "quick-status is-error";
        }
      } finally {
        if (submit) submit.disabled = false;
      }
    });
  }

  // PWA install -----------------------------------------------------------
  let deferredPrompt = null;
  const installButton = document.getElementById("pwa-install");

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredPrompt = event;
    if (installButton) installButton.hidden = false;
  });

  if (installButton) {
    installButton.addEventListener("click", async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      installButton.hidden = true;
    });
  }

  window.addEventListener("appinstalled", () => {
    if (installButton) installButton.hidden = true;
  });

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch((error) => {
        console.error("Service worker registration failed", error);
      });
    });
  }
})();
