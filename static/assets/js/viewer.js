(function () {
      // 允许查看的项目：新增项目时在这里补一条
      var PROJECTS = {
        'arctic-ink': { title: 'Arctic Ink', path: 'projects/arctic-ink/' },
        'ibus-rime': { title: 'ibus-rime', path: 'projects/ibus-rime/' }
      };

      var codeEl = document.getElementById('code');
      var nameEl = document.getElementById('filename');
      var metaEl = document.getElementById('meta');
      var toolbar = document.getElementById('toolbar');
      var downloadEl = document.getElementById('download');
      var copyEl = document.getElementById('copy');
      var backEl = document.getElementById('back');

      function formatSize(bytes) {
        if (!bytes) return '';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(bytes < 10240 ? 1 : 0) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
      }

      function fail(message) {
        nameEl.textContent = '打不开这个文件';
        metaEl.textContent = message;
        codeEl.textContent = '';
        toolbar.hidden = true;
      }

      var params = new URLSearchParams(location.search);
      var key = params.get('p') || '';
      var file = params.get('f') || 'install.sh';
      var project = PROJECTS[key];

      if (!project) return fail('项目参数不对，请从项目页进入。');
      if (!/^[A-Za-z0-9][A-Za-z0-9._\/-]*$/.test(file) || file.indexOf('..') !== -1) {
        return fail('文件参数不对，请从项目页进入。');
      }

      var url = project.path + 'files/' + file;

      nameEl.textContent = file;
      document.title = file + ' · ' + project.title;
      metaEl.textContent = '来自 ' + project.title + ' 的原始文件。';
      backEl.href = project.path;
      backEl.textContent = '← ' + project.title;
      downloadEl.href = url;
      toolbar.hidden = false;

      fetch(url, { cache: 'no-cache' })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          var size = formatSize(Number(res.headers.get('content-length')));
          if (size) metaEl.textContent = '来自 ' + project.title + ' · ' + size;
          return res.text();
        })
        .then(function (text) {
          var lines = text.replace(/\n$/, '').split('\n');
          var frag = document.createDocumentFragment();
          lines.forEach(function (line) {
            var span = document.createElement('span');
            span.className = 'line';
            span.textContent = line;
            frag.appendChild(span);
          });
          codeEl.textContent = '';
          codeEl.appendChild(frag);

          copyEl.addEventListener('click', function () {
            if (!navigator.clipboard) {
              copyEl.textContent = '浏览器不支持复制';
              return;
            }
            navigator.clipboard.writeText(text).then(function () {
              copyEl.textContent = '已复制';
              setTimeout(function () { copyEl.textContent = '复制内容'; }, 1600);
            }).catch(function () {
              copyEl.textContent = '复制失败';
            });
          });
        })
        .catch(function (err) {
          fail('读取失败（' + err.message + '）。');
        });
    })();
