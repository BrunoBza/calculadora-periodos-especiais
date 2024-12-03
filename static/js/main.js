// Template para um novo período
function templatePeriodo(id) {
    return `
        <div class="periodo border rounded p-3 mb-3" data-id="${id}">
            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">Data Início</label>
                    <input type="date" class="form-control" name="data_inicio" required
                           data-date-format="DD/MM/YYYY" placeholder="DD/MM/AAAA"
                           onchange="formatarDataInput(this)">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Data Fim</label>
                    <input type="date" class="form-control" name="data_fim" required
                           data-date-format="DD/MM/YYYY" placeholder="DD/MM/AAAA"
                           onchange="formatarDataInput(this)">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Agente Nocivo</label>
                    <select class="form-select" name="agente" required>
                        <option value="">Selecione...</option>
                        <option value="ruido">Ruído</option>
                        <option value="agentes_quimicos">Agentes Químicos</option>
                        <option value="vibracao">Vibração</option>
                        <option value="calor">Calor</option>
                        <option value="radiacao">Radiação</option>
                        <option value="eletricidade">Eletricidade</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <label class="form-label">Intensidade</label>
                    <input type="number" step="0.1" class="form-control" name="intensidade" required>
                </div>
                <div class="col-md-1 d-flex align-items-end">
                    <button type="button" class="btn btn-danger" onclick="removerPeriodo(${id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

let contadorPeriodos = 0;

// Função para formatar data do formato YYYY-MM-DD para DD/MM/YYYY
function formatarData(data) {
    if (!data) return '';
    const [ano, mes, dia] = data.split('-');
    return `${dia.padStart(2, '0')}/${mes.padStart(2, '0')}/${ano}`;
}

// Função para converter data de DD/MM/YYYY para YYYY-MM-DD
function converterDataParaISO(data) {
    if (!data) return '';
    const [dia, mes, ano] = data.split('/');
    return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
}

// Função para formatar o valor do input de data
function formatarDataInput(input) {
    if (!input.value) return;
    const dataFormatada = formatarData(input.value);
    input.setAttribute('data-valor-formatado', dataFormatada);
}

// Adiciona um novo período ao formulário
function adicionarPeriodo() {
    const periodos = document.getElementById('periodos');
    contadorPeriodos++;
    periodos.insertAdjacentHTML('beforeend', templatePeriodo(contadorPeriodos));
}

// Remove um período do formulário
function removerPeriodo(id) {
    const periodo = document.querySelector(`.periodo[data-id="${id}"]`);
    periodo.remove();
}

// Copia a minuta para a área de transferência
function copiarMinuta() {
    const minuta = document.getElementById('minuta').textContent;
    navigator.clipboard.writeText(minuta)
        .then(() => alert('Minuta copiada para a área de transferência!'))
        .catch(err => console.error('Erro ao copiar minuta:', err));
}

// Processa o formulário
document.getElementById('periodoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const periodos = Array.from(document.querySelectorAll('.periodo')).map(periodo => {
        const dataInicio = periodo.querySelector('[name="data_inicio"]');
        const dataFim = periodo.querySelector('[name="data_fim"]');
        
        return {
            data_inicio: dataInicio.getAttribute('data-valor-formatado') || formatarData(dataInicio.value),
            data_fim: dataFim.getAttribute('data-valor-formatado') || formatarData(dataFim.value),
            agente: periodo.querySelector('[name="agente"]').value,
            intensidade: periodo.querySelector('[name="intensidade"]').value
        };
    });

    try {
        const response = await fetch('/avaliar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ periodos })
        });

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Exibe os resultados
        const resultadosDiv = document.getElementById('resultados');
        resultadosDiv.innerHTML = data.resultados.map(resultado => {
            const periodo = resultado.periodo_original;
            const subperiodo = resultado.subperiodo;
            
            return `
                <div class="alert ${subperiodo.eh_especial ? 'alert-success' : 'alert-danger'} mb-3">
                    <p class="mb-1"><strong>Período:</strong> ${subperiodo.data_inicio} a ${subperiodo.data_fim}</p>
                    <p class="mb-1"><strong>Agente:</strong> ${periodo.agente.replace('_', ' ').charAt(0).toUpperCase() + periodo.agente.slice(1)}</p>
                    <p class="mb-1"><strong>Limite no período:</strong> >${subperiodo.limite} ${subperiodo.unidade}</p>
                    <p class="mb-1"><strong>Intensidade informada:</strong> ${subperiodo.intensidade} ${subperiodo.unidade}</p>
                    <p class="mb-0"><strong>Resultado:</strong> ${subperiodo.eh_especial ? 'Período Especial' : 'Período Não Especial'}</p>
                    ${subperiodo.detalhes ? Object.entries(subperiodo.detalhes).map(([chave, valor]) => 
                        `<p class="mb-0"><strong>${chave}:</strong> ${valor}</p>`).join('') : ''}
                </div>
            `;
        }).join('');
        
        // Mostra os cards de resultado e minuta
        document.getElementById('resultadosCard').classList.remove('d-none');
        document.getElementById('minutaCard').classList.remove('d-none');
        
        // Atualiza a minuta
        document.getElementById('minuta').textContent = data.minuta;

    } catch (error) {
        console.error('Erro ao processar períodos:', error);
        alert(error.message || 'Erro ao processar períodos. Verifique o console para mais detalhes.');
    }
});

// Adiciona o primeiro período automaticamente
adicionarPeriodo();
