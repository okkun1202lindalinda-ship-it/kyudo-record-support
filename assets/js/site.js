const toggle = document.querySelector("[data-nav-toggle]");
const navigation = document.querySelector("[data-site-nav]");

if (toggle && navigation) {
  toggle.addEventListener("click", () => {
    const isOpen = navigation.dataset.open === "true";
    navigation.dataset.open = String(!isOpen);
    toggle.setAttribute("aria-expanded", String(!isOpen));
    toggle.setAttribute(
      "aria-label",
      isOpen ? "メニューを開く" : "メニューを閉じる",
    );
  });

  navigation.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      navigation.dataset.open = "false";
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "メニューを開く");
    }
  });
}

for (const year of document.querySelectorAll("[data-current-year]")) {
  year.textContent = new Date().getFullYear().toString();
}
