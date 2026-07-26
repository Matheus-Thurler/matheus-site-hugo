(function () {
  var STORAGE_KEY = 'mt-admin-sidebar-scroll';

  function getSidebarScroller() {
    return document.querySelector('.app-sidebar .sidebar-wrapper');
  }

  function saveScroll() {
    var el = getSidebarScroller();
    if (el) {
      sessionStorage.setItem(STORAGE_KEY, String(el.scrollTop));
    }
  }

  function restoreScroll() {
    var el = getSidebarScroller();
    var saved = sessionStorage.getItem(STORAGE_KEY);
    if (!el || saved === null) {
      return;
    }
    el.scrollTop = parseInt(saved, 10) || 0;
  }

  function markActiveLink() {
    var path = window.location.pathname;
    document.querySelectorAll('#jazzy-navigation a.nav-link[href]').forEach(function (link) {
      var href = link.getAttribute('href');
      if (!href || href === '#' || href.indexOf('javascript:') === 0) {
        return;
      }
      if (path === href || (href.length > 1 && path.indexOf(href) === 0)) {
        link.classList.add('active');
        var tree = link.closest('.nav-treeview');
        if (tree) {
          var parent = tree.closest('.has-treeview');
          if (parent) {
            parent.classList.add('menu-open');
          }
        }
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    restoreScroll();
    markActiveLink();

    var scroller = getSidebarScroller();
    if (scroller) {
      scroller.addEventListener('scroll', saveScroll, { passive: true });
    }

    document.querySelectorAll('#jazzy-navigation a.nav-link[href]').forEach(function (link) {
      link.addEventListener('click', saveScroll);
    });

    window.addEventListener('beforeunload', saveScroll);
  });
})();
