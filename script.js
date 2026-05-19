const copyButtons = document.querySelectorAll("[data-copy-target]");

copyButtons.forEach((button) => {
  const defaultLabel = button.textContent;

  button.addEventListener("click", async () => {
    const targetId = button.getAttribute("data-copy-target");
    const target = targetId ? document.getElementById(targetId) : null;

    if (!target) {
      return;
    }

    try {
      await navigator.clipboard.writeText(target.innerText);
      button.textContent = "Copied";
      window.setTimeout(() => {
        button.textContent = defaultLabel;
      }, 1400);
    } catch {
      button.textContent = "Select text";
      window.setTimeout(() => {
        button.textContent = defaultLabel;
      }, 1600);
    }
  });
});
