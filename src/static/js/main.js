const el = id => document.getElementById(id);
const show = e => e?.classList.remove('hidden');
const hide = e => e?.classList.add('hidden');
const buildRow = (t, c) => `<tr>${c.map(v => `<${t}>${v}</${t}>`).join('')}</tr>`;

const postJSON = (url, body) => fetch(url, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
}).then(r => r.json());

const readFile = f => new Promise((res, rej) => {
    const r = new FileReader(); r.onload = e => res(e.target.result); r.onerror = rej; r.readAsText(f, 'UTF-8');
});

const parseCSV = t => t.trim().split(/\r?\n/).map(l => l.split(',').map(s => s.trim()));

function parseMcaData(critText, altText) {
    const cRows = parseCSV(critText), aRows = parseCSV(altText), h = cRows[0].map(v => v.toLowerCase());
    return {
        criteria: cRows.slice(1).filter(r => r[0]).map(r => ({ name: r[h.indexOf('name')], weight: parseFloat(r[h.indexOf('weight')]) || 0, type: r[h.indexOf('type')] || 'min' })),
        alternatives: aRows.slice(1).filter(r => r[0]).map(r => ({ name: r[0], values: r.slice(1).map(v => parseFloat(v) || 0) }))
    };
}

function setupDropZone(zoneId, inputId, onFile) {
    const zone = el(zoneId), input = el(inputId);
    if (!zone || !input) return;
    input.onchange = () => input.files[0] && onFile(input.files[0]);
    zone.ondragover = e => { e.preventDefault(); zone.classList.add('drag-over'); };
    zone.ondragleave = () => zone.classList.remove('drag-over');
    zone.ondrop = e => { e.preventDefault(); zone.classList.remove('drag-over'); e.dataTransfer.files[0] && onFile(e.dataTransfer.files[0]); };
}

// Function to render a read-only table preview
function renderTablePreview(containerId, csvRows, isVotes = false) {
    const container = el(containerId);
    if (!container || !csvRows || csvRows.length === 0) return;

    let html = '<table><thead>';

    if (isVotes) {
        // For Borda / Nanson: Generate "Expert 1, Expert 2..." for columns
        const expertHeaders = csvRows.map((_, idx) => `Expert ${idx + 1}`);
        html += buildRow('th', expertHeaders);
        html += '</thead><tbody>';

        // Correctly extracting the i-th element from each expert row
        const maxRankings = Math.max(...csvRows.map(r => r.length));
        for (let i = 0; i < maxRankings; i++) {
            const rowData = csvRows.map(r => r[i] || '');
            html += buildRow('td', rowData);
        }
    } else {
        // Standard rendering for criteria and alternatives (with original header)
        html += buildRow('th', csvRows[0]);
        html += '</thead><tbody>';
        for (let i = 1; i < csvRows.length; i++) {
            if (csvRows[i].some(cell => cell !== '')) {
                html += buildRow('td', csvRows[i]);
            }
        }
    }

    html += '</tbody></table>';
    container.innerHTML = html;
    show(container);
}

window.switchTab = function(name) {
    document.querySelectorAll('.tab-content, .tab-btn').forEach(t => {
        t.classList.remove('active');
        if (t.classList.contains('tab-content')) t.classList.add('hidden');
    });

    if (window.event?.target) {
        window.event.target.classList.add('active');
    } else {
        Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(name))?.classList.add('active');
    }

    const activeTab = el(`tab-${name}`);
    if (activeTab) {
        activeTab.classList.add('active');
        activeTab.classList.remove('hidden');
    }
};

// BORDA / NANSON
(function () {
    let votes = null;
    setupDropZone('bn-drop-zone', 'bn-file-input', async f => {
        el('bn-file-name').textContent = `✓ ${f.name}`;
        show(el('bn-file-name'));
        const rows = parseCSV(await readFile(f)).filter(r => r[0]);
        votes = rows;
        renderTablePreview('bn-preview', rows, true);
    });

    el('calculate-btn').onclick = async () => {
        if (!votes) return show(Object.assign(el('error-msg'), { textContent: 'Select file.' }));
        hide(el('error-msg')); const d = await postJSON('/calculate', { votes });
        hide(el('results-placeholder')); show(el('results-section')); el('paradox-banner').classList.toggle('hidden', !d.paradox);

        ['borda', 'nanson'].forEach(m => { el(`${m}-winner`).textContent = `Winner: ${d[m].winner}`; el(`${m}-winner`).className = `winner-box ${d.paradox ? 'paradox' : 'normal'}`; });
        el('borda-scores').innerHTML = Object.entries(d.borda.scores).sort((a, b) => b[1] - a[1]).map(([a, p]) => buildRow('td', [a, p])).join('');
        el('nanson-rounds').innerHTML = d.nanson.rounds.map((r, i) => `<div class="round-block"><div class="round-title">Round ${i + 1} ${r.eliminated.map(e => `<span class="eliminated-tag">-${e}</span>`).join('')}</div><div>${Object.entries(r.scores).sort((a, b) => b[1] - a[1]).map(([a, p]) => `${a}: ${p}`).join(' · ')}</div><div class="avg-label">Average Score: ${r.avg}</div></div>`).join('');
    };
})();

// TOPSIS
(function () {
    let tCritText = null, tAltText = null, topsisData = null;
    const load = async () => {
        if (tCritText && tAltText) {
            try { topsisData = parseMcaData(tCritText, tAltText); hide(el('topsis-error-msg')); }
            catch (e) { show(Object.assign(el('topsis-error-msg'), { textContent: e.message })); }
        }
    };
    setupDropZone('topsis-crit-drop-zone', 'topsis-crit-file-input', async f => {
        tCritText = await readFile(f);
        el('topsis-crit-file-name').textContent = `✓ ${f.name}`;
        show(el('topsis-crit-file-name'));
        renderTablePreview('topsis-crit-preview', parseCSV(tCritText));
        load();
    });
    setupDropZone('topsis-alt-drop-zone', 'topsis-alt-file-input', async f => {
        tAltText = await readFile(f);
        el('topsis-alt-file-name').textContent = `✓ ${f.name}`;
        show(el('topsis-alt-file-name'));
        renderTablePreview('topsis-alt-preview', parseCSV(tAltText));
        load();
    });

    el('topsis-calculate-btn').onclick = async () => {
        if (!topsisData) return show(Object.assign(el('topsis-error-msg'), { textContent: 'Upload files.' }));
        const w = topsisData.criteria.map(c => c.weight);
        if (Math.abs(w.reduce((a, b) => a + b, 0) - 1.0) > 0.01) return show(Object.assign(el('topsis-error-msg'), { textContent: 'Weights sum must be 1.0' }));
        hide(el('topsis-error-msg'));

        const p = { alternatives: topsisData.alternatives, weights: w, criteria_types: topsisData.criteria.map(c => c.type) };
        const r = await postJSON('/topsis', p);

        hide(el('topsis-placeholder')); show(el('topsis-results-section'));
        el('topsis-winner-box').textContent = `Best: ${r.results[0].name} (${r.results[0].score})`;
        el('topsis-scores').innerHTML = r.results.map(x => `<tr><td><span class="rank-badge ${x.rank === 1 ? 'gold' : ''}">${x.rank}</span></td><td>${x.name}</td><td>${x.score}</td><td>${x.dist_best}</td><td>${x.dist_worst}</td></tr>`).join('');
    };
})();

// ELECTRE I
(function () {
    let eCritText = null, eAltText = null, electreData = null;
    const load = async () => {
        if (eCritText && eAltText) {
            try { electreData = parseMcaData(eCritText, eAltText); hide(el('electre-error-msg')); }
            catch (e) { show(Object.assign(el('electre-error-msg'), { textContent: e.message })); }
        }
    };
    setupDropZone('electre-crit-drop-zone', 'electre-crit-file-input', async f => {
        eCritText = await readFile(f);
        el('electre-crit-file-name').textContent = `✓ ${f.name}`;
        show(el('electre-crit-file-name'));
        renderTablePreview('electre-crit-preview', parseCSV(eCritText));
        load();
    });
    setupDropZone('electre-alt-drop-zone', 'electre-alt-file-input', async f => {
        eAltText = await readFile(f);
        el('electre-alt-file-name').textContent = `✓ ${f.name}`;
        show(el('electre-alt-file-name'));
        renderTablePreview('electre-alt-preview', parseCSV(eAltText));
        load();
    });

    el('electre-calculate-btn').onclick = async () => {
        if (!electreData) return show(Object.assign(el('electre-error-msg'), { textContent: 'Upload files.' }));
        const w = electreData.criteria.map(c => c.weight);
        hide(el('electre-error-msg'));

        const p = { alternatives: electreData.alternatives, weights: w, criteria_types: electreData.criteria.map(c => c.type) };
        const r = await postJSON('/electre', { ...p, c_threshold: el('electre-c').value, d_threshold: el('electre-d').value });

        hide(el('electre-placeholder')); show(el('electre-results-section'));
        el('electre-kernel-box').textContent = `Kernel: ${r.kernel.join(', ') || 'None'}`;
        el('electre-relations').innerHTML = r.relations.map(x => `<div>• <strong>${x.from}</strong> outranks <strong>${x.to}</strong></div>`).join('') || 'No relations.';
        const renderMtx = (h, b, m) => { el(h).innerHTML = buildRow('th', ['-', ...r.names]); el(b).innerHTML = r.names.map((n, ri) => buildRow('td', [`<strong>${n}</strong>`, ...r.names.map((_, ci) => ri === ci ? '-' : m[ri][ci])])).join(''); };
        renderMtx('c-matrix-head', 'c-matrix-body', r.concordance); renderMtx('d-matrix-head', 'd-matrix-body', r.discordance);
    };
})();

// CBIM
(function () {
    let cCritText = null, cAltText = null, data = null;
    const load = async () => {
        if (!cCritText || !cAltText) return;
        try {
            data = parseMcaData(cCritText, cAltText); hide(el('cbim-file-error'));
            el('cbim-base-select').innerHTML = data.alternatives.map((a, i) => `<option value="${i}">${a.name}</option>`).join('');
            el('cbim-preferences-container').innerHTML = data.criteria.map((c, i) => `<div class="cbim-pref-row"><span class="cbim-crit-label">${c.name}:</span><select class="cbim-action" data-idx="${i}"><option value="none">None</option><option value="improve">Improve</option><option value="worsen">Worsen</option></select><input type="number" class="cbim-delta hidden" id="cbim-delta-${i}" placeholder="Delta"></div>`).join('');
            document.querySelectorAll('.cbim-action').forEach(s => s.onchange = e => el(`cbim-delta-${e.target.dataset.idx}`).classList.toggle('hidden', e.target.value !== 'worsen'));
            show(el('cbim-settings-section'));
        } catch (e) { show(Object.assign(el('cbim-file-error'), { textContent: e.message })); }
    };
    setupDropZone('cbim-crit-drop-zone', 'cbim-crit-file-input', async f => {
        cCritText = await readFile(f);
        el('cbim-crit-file-name').textContent = `✓ ${f.name}`;
        show(el('cbim-crit-file-name'));
        renderTablePreview('cbim-crit-preview', parseCSV(cCritText));
        load();
    });
    setupDropZone('cbim-alt-drop-zone', 'cbim-alt-file-input', async f => {
        cAltText = await readFile(f);
        el('cbim-alt-file-name').textContent = `✓ ${f.name}`;
        show(el('cbim-alt-file-name'));
        renderTablePreview('cbim-alt-preview', parseCSV(cAltText));
        load();
    });

    el('cbim-calculate-btn').onclick = async () => {
        if (!data) return show(Object.assign(el('cbim-file-error'), { textContent: 'Upload files.' }));
        const prefs = Array.from(document.querySelectorAll('.cbim-action')).map((s, i) => ({ action: s.value, delta: s.value === 'worsen' ? parseFloat(el(`cbim-delta-${i}`)?.value || 0) : 0 }));
        const d = await postJSON('/api/cbim', { matrix: data.alternatives.map(a => a.values), alternatives: data.alternatives.map(a => a.name), criteria_types: data.criteria.map(c => c.type), base_idx: el('cbim-base-select').value, l_count: el('cbim-l-count').value, preferences: prefs });
        if (!d.success) return alert(d.error);
        hide(el('cbim-placeholder')); show(el('cbim-results-section'));
        el('cbim-winner-box').textContent = d.results.length ? `Favorite: ${d.results[0].name}` : 'No alternatives satisfy conditions.';
        el('cbim-table-body').innerHTML = d.results.map(r => `<tr><td><strong>${r.name}</strong></td><td>${r.score}</td><td>[ ${r.values.join(', ')} ]</td></tr>`).join('');
    };
})();
