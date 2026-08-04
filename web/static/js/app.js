let currentSteps = [];
let currentStepIdx = 0;
let totalSteps = 0;

const examples = {
  estandar: `MAX z = -3 x1 - 2 x2\ns.t.\nx1 + 2 x2 >= 6\n2 x1 + x2 >= 8\nx1, x2 >= 0`,
  infactible: `MAX z = -x1 - x2\ns.t.\n-x1 - x2 <= -5\nx1 + x2 <= 2\nx1, x2 >= 0`,
  tres_vars: `MAX z = -3 x1 - 4 x2 - 1 x3\ns.t.\n-x1 - 2 x2 - x3 <= -6\n-2 x1 - x2 - 3 x3 <= -8\nx1, x2, x3 >= 0`
};

function loadExample() {
  const select = document.getElementById("example-select");
  const key = select.value;
  if (examples[key]) {
    document.getElementById("lp-input").value = examples[key];
  }
}

async function solveProblem() {
  const text = document.getElementById("lp-input").value.trim();
  const mode = document.getElementById("mode-select").value;
  const pivot_rule = document.getElementById("pivot-select").value;

  if (!text) {
    alert("Por favor ingrese la descripción del problema.");
    return;
  }

  try {
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, mode, pivot_rule })
    });

    const data = await res.json();
    if (!data.success) {
      alert("Error al procesar el problema: " + data.error);
      return;
    }

    currentSteps = data.steps;
    totalSteps = data.total_steps;
    currentStepIdx = 0;

    document.getElementById("placeholder-card").style.display = "none";
    document.getElementById("results-card").style.display = "block";

    renderStep(currentStepIdx);

  } catch (err) {
    alert("Error de conexión con el servidor: " + err.message);
  }
}

function goToStep(idx) {
  if (idx >= 0 && idx < totalSteps) {
    currentStepIdx = idx;
    renderStep(currentStepIdx);
  }
}

function prevStep() {
  goToStep(currentStepIdx - 1);
}

function nextStep() {
  goToStep(currentStepIdx + 1);
}

function renderStep(idx) {
  const step = currentSteps[idx];
  document.getElementById("step-indicator").innerText = `Iteración ${step.iteration} (Paso ${idx + 1} de ${totalSteps})`;

  document.getElementById("btn-first").disabled = (idx === 0);
  document.getElementById("btn-prev").disabled = (idx === 0);
  document.getElementById("btn-next").disabled = (idx === totalSteps - 1);
  document.getElementById("btn-last").disabled = (idx === totalSteps - 1);

  // 1. Renderizar Diccionario de Dantzig
  const dictBox = document.getElementById("dictionary-box");
  let dictHtml = `<div class="math-z">${step.dictionary.z_equation}</div>`;
  step.dictionary.equations.forEach(eq => {
    dictHtml += `<div class="math-eq">${eq}</div>`;
  });
  dictBox.innerHTML = dictHtml;

  // 2. Renderizar Tabla Simplex Canónica
  const table = document.getElementById("tableau-table");
  const tabData = step.tableau;
  
  let tabHtml = '<thead><tr><th>Base</th>';
  tabData.headers.forEach(h => {
    let extraClass = '';
    if (h === step.entering_var) extraClass = 'entering-col';
    tabHtml += `<th class="${extraClass}">${h}</th>`;
  });
  tabHtml += '</tr></thead><tbody>';

  // Fila Z
  tabHtml += '<tr class="z-row"><td>Z</td>';
  tabData.z_row.forEach((val, cIdx) => {
    const colHeader = tabData.headers[cIdx];
    let extraClass = (colHeader === step.entering_var) ? 'entering-col' : '';
    tabHtml += `<td class="${extraClass}">${val}</td>`;
  });
  tabHtml += '</tr>';

  // Filas de Restricciones
  tabData.rows.forEach(r => {
    const isLeaving = (r.var === step.leaving_var);
    tabHtml += '<tr>';
    tabHtml += `<td style="font-weight:bold; color: var(--accent-primary);">${r.var}</td>`;
    
    r.row.forEach((val, cIdx) => {
      const colHeader = tabData.headers[cIdx];
      const isEntering = (colHeader === step.entering_var);
      
      let classes = [];
      if (isLeaving) classes.push('leaving-row');
      if (isEntering) classes.push('entering-col');
      if (isLeaving && isEntering) classes.push('pivot-cell');
      
      tabHtml += `<td class="${classes.join(' ')}">${val}</td>`;
    });
    
    tabHtml += '</tr>';
  });

  tabHtml += '</tbody>';
  table.innerHTML = tabHtml;

  // 3. Renderizar Explicación y Criterios
  const expBox = document.getElementById("explanation-box");
  const expTitle = document.getElementById("exp-title");
  const expContent = document.getElementById("exp-content");

  expBox.className = "explanation-box";

  if (step.status === "OPTIMAL") {
    expBox.classList.add("status-optimal");
    expTitle.innerHTML = '🎉 ¡Solución Óptima Encontrada!';
    
    let solHtml = '<ul>';
    for (const [v, val] of Object.entries(step.primal_solution)) {
      solHtml += `<li><b>${v}</b> = ${val}</li>`;
    }
    solHtml += '</ul>';
    solHtml += `<p style="margin-top:0.5rem;"><b>Valor Óptimo Z:</b> ${step.objective_value}</p>`;

    expContent.innerHTML = `
      <p style="margin-bottom:0.5rem;">Todas las variables básicas son no negativas (<i>b<sub>i</sub> ≥ 0</i>) y el diccionario mantiene factibilidad dual (coeficientes en <i>z ≤ 0</i>).</p>
      ${solHtml}
    `;

  } else if (step.status === "INFEASIBLE") {
    expBox.classList.add("status-infeasible");
    expTitle.innerHTML = '⚠️ ¡Problema Infactible (Dual No Acotado)!';
    expContent.innerHTML = `
      <p>La variable de salida <span class="badge badge-sale">${step.leaving_var}</span> tiene constante negativa en el lado derecho, pero ningún coeficiente no básico en su fila es positivo (<i>d<sub>${step.leaving_var}, j</sub> ≤ 0</i>).</p>
      <p style="margin-top:0.5rem;">Por tanto, no es posible recuperar la factibilidad primal manteniendo la factibilidad dual.</p>
    `;

  } else if (step.status === "NOT_DUAL_FEASIBLE") {
    expBox.classList.add("status-infeasible");
    expTitle.innerHTML = '🛑 Error: Diccionario Inicial No Es Dual-Factible';
    expContent.innerHTML = `<p>${step.explanation}</p>`;

  } else {
    expTitle.innerHTML = `Criterios de Transición para Iteración ${step.iteration + 1}`;
    
    let ratioRows = '';
    for (const [nbVar, ratio] of Object.entries(step.ratio_tests)) {
      const isEntra = (nbVar === step.entering_var);
      const highlight = isEntra ? 'style="font-weight:bold; color: var(--accent-success);"' : '';
      ratioRows += `<tr ${highlight}>
        <td>${nbVar}</td>
        <td>${ratio !== null ? ratio : 'No elegible (d ≤ 0)'}</td>
        <td>${isEntra ? '✅ Seleccionada (Mínimo cociente)' : ''}</td>
      </tr>`;
    }

    expContent.innerHTML = `
      <div style="margin-bottom: 0.75rem;">
        <div><b>1. Variable que Sale (x<sub>sale</sub>):</b> <span class="badge badge-sale">${step.leaving_var}</span> (Fila infactible con constante b < 0)</div>
        <div style="margin-top: 0.25rem;"><b>2. Variable que Entra (x<sub>entra</sub>):</b> <span class="badge badge-entra">${step.entering_var}</span> (Test del cociente dual mínimo)</div>
        <div style="margin-top: 0.25rem;"><b>3. Elemento Pivote:</b> <code>${step.pivot_element}</code></div>
      </div>
      
      <div style="font-weight: 600; font-size: 0.85rem; margin-top: 0.5rem; color: var(--text-muted);">Tabla de Test del Cociente Dual (θ<sub>j</sub> = |c<sub>j</sub> / d<sub>sale, j</sub>|):</div>
      <table class="ratio-table">
        <thead><tr><th>Variable No Básica</th><th>Cociente Dual (θ<sub>j</sub>)</th><th>Resultado</th></tr></thead>
        <tbody>${ratioRows}</tbody>
      </table>
    `;
  }
}

function exportMarkdown() {
  if (!currentSteps.length) return;

  let md = "# Reporte de Resolución - Método Simplex Dual\n\n";
  currentSteps.forEach((step, idx) => {
    md += `## Iteración ${step.iteration}\n\n`;
    md += `### Diccionario de Dantzig\n\`\`\`text\n${step.dictionary.z_equation}\n`;
    step.dictionary.equations.forEach(eq => md += `${eq}\n`);
    md += `\`\`\`\n\n`;

    if (step.status === "OPTIMAL") {
      md += `### Resultado: SOLUCIÓN ÓPTIMA\n\n`;
      md += `**Valor Óptimo Z:** ${step.objective_value}\n\n`;
      md += `**Variables:**\n`;
      for (const [k, v] of Object.entries(step.primal_solution)) {
        md += `- **${k}**: ${v}\n`;
      }
    } else if (step.status === "INFEASIBLE") {
      md += `### Resultado: PROBLEMA INFACTIBLE (DUAL NO ACOTADO)\n\n`;
      md += `${step.explanation}\n\n`;
    } else if (step.leaving_var) {
      md += `### Transición:\n`;
      md += `- **Variable que sale:** ${step.leaving_var}\n`;
      md += `- **Variable que entra:** ${step.entering_var}\n`;
      md += `- **Pivote:** ${step.pivot_element}\n\n`;
    }
    md += `---\n\n`;
  });

  const blob = new Blob([md], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "simplex_dual_report.md";
  a.click();
}
