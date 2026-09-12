import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/execute'

const STARTER_CODE = `fn main() {
    let mut x: i32 = 10;
    let y: i32 = 20;
 
    if x < y {
        x = x + y;
    } else {
        x = x - y;
    }
 
    while x > 0 {
        x = x - 1;
    }
 
    println(x);
}
`

function useLineCount(text) {
  return useMemo(() => text.split('\n').length, [text])
}

function IconButton({ children, label, onClick, tone = 'default', disabled }) {
  return (
    <button
      type="button"
      className={`btn btn--${tone}`}
      onClick={onClick}
      disabled={disabled}
      title={label}
    >
      {children}
      <span>{label}</span>
    </button>
  )
}

export default function App() {
  const [code, setCode] = useState(STARTER_CODE)
  const [savedCode, setSavedCode] = useState(STARTER_CODE)
  const [fileName, setFileName] = useState('principal.ox')
  const [consoleLines, setConsoleLines] = useState([
    { type: 'hint', text: '> Escriba el codigo y presione "Ejecutar" para comenzar' },
  ])
  const [isRunning, setIsRunning] = useState(false)
  const [reportTab, setReportTab] = useState('errors')
  const [result, setResult] = useState({ errors: [], symbols: [], ast: [], ast_image: '' })

  const textareaRef = useRef(null)
  const gutterRef = useRef(null)
  const fileInputRef = useRef(null)
  const reportsRef = useRef(null)

  const lineCount = useLineCount(code)
  const isDirty = code !== savedCode
  const errorLines = useMemo(
    () => new Set(result.errors.map((e) => e.linea)),
    [result.errors]
  )

  useEffect(() => {
    document.title = `OxigenScript`
  }, [])

  const handleScrollSync = () => {
    if (gutterRef.current && textareaRef.current) {
      gutterRef.current.scrollTop = textareaRef.current.scrollTop
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault()
      const el = e.target
      const start = el.selectionStart
      const end = el.selectionEnd
      const next = code.slice(0, start) + '    ' + code.slice(end)
      setCode(next)
      requestAnimationFrame(() => {
        el.selectionStart = el.selectionEnd = start + 4
      })
    }
  }

  const appendConsole = (type, text) => {
    setConsoleLines((prev) => [...prev, { type, text }])
  }

  const handleNuevo = () => {
    if (isDirty && !window.confirm('Hay cambios sin guardar. ¿Desea crear un archivo nuevo?')) {
      return
    }
    setCode('fn main() {\n    \n}\n')
    setSavedCode('fn main() {\n    \n}\n')
    setFileName('principal.ox')
    setConsoleLines([{ type: 'hint', text: '> Archivo nuevo creado.' }])
    setResult({ errors: [], symbols: [], ast: [] })
  }

  const handleAbrir = () => fileInputRef.current?.click()

  const handleFileSelected = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      const text = String(reader.result ?? '')
      setCode(text)
      setSavedCode(text)
      setFileName(file.name)
      appendConsole('hint', `> Archivo "${file.name}" cargado.`)
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleGuardar = () => {
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName || 'principal.ox'
    a.click()
    URL.revokeObjectURL(url)
    setSavedCode(code)
    appendConsole('hint', `> Archivo guardado como "${fileName}".`)
  }

  const handleEjecutar = async () => {
    setIsRunning(true)
    setConsoleLines([])
    appendConsole('info', '> Ejecutando OxigenScript...')

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo: code }),
      })
      if (!res.ok) throw new Error('Respuesta no valida del servidor')
      const data = await res.json()

      setResult({
        errors: data.errores ?? [],
        symbols: data.symbols ?? [],
        ast: data.ast ?? [],
        ast_image: data.ast_image || '',
      })

      if ((data.errores ?? []).length === 0) {
        appendConsole('success', 'Compilacion exitosa.')
      } else {
        appendConsole('error', `Se encontraron ${data.errores.length} error(es).`)
      }

      // Muestra siempre la salida, con o sin errores
      appendConsole('output', '--- Programa en ejecucion ---')
      ;(data.salida ?? []).forEach((line) => appendConsole('output', line))
      appendConsole('output', '--- Fin de la ejecucion ---')
      appendConsole('meta', `Tiempo de ejecucion: ${data.tiempo ?? '—'}`)
    } catch (err) {
      appendConsole('error', `Error de conexion: ${err.message}`)
    } finally {
      setIsRunning(false)
    }
  }

  const handleReportesClick = () => {
    reportsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }

  return (
    <div className="app">
      <header className="toolbar">
        <div className="brand">
          <span className="brand__name">OxigenScript</span>
        </div>

        <div className="toolbar__actions">
          <IconButton label="Nuevo" onClick={handleNuevo}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </IconButton>
          <IconButton label="Abrir" onClick={handleAbrir}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /></svg>
          </IconButton>
          <IconButton label="Guardar" onClick={handleGuardar}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 4h11l3 3v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /><path d="M8 4v5h7V4M8 14h8v6H8v-6Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /></svg>
          </IconButton>
          <IconButton label="Reportes" onClick={handleReportesClick}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /><path d="M9 12h6M9 16h6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </IconButton>
          <IconButton label={isRunning ? 'Ejecutando…' : 'Ejecutar'} onClick={handleEjecutar} tone="accent" disabled={isRunning}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M7 4.5v15l13-7.5-13-7.5Z" fill="currentColor" /></svg>
          </IconButton>
        </div>
      </header>

      <div className={`run-pulse ${isRunning ? 'run-pulse--active' : ''}`} aria-hidden="true" />

      <main className="workspace">
        <section className="editor" aria-label="Editor de codigo">
          <div className="panel__label">
            <span>Editor</span>
            <span className="panel__label-sub">OxigenScript · {lineCount} lineas</span>
          </div>
          <div className="editor__body">
            <div className="editor__gutter" ref={gutterRef}>
              {Array.from({ length: lineCount }, (_, i) => i + 1).map((n) => (
                <div key={n} className={`editor__gutter-line ${errorLines.has(n) ? 'editor__gutter-line--error' : ''}`}>
                  {errorLines.has(n) && <span className="editor__gutter-dot" />}
                  {n}
                </div>
              ))}
            </div>
            <textarea
              ref={textareaRef}
              className="editor__textarea"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onScroll={handleScrollSync}
              onKeyDown={handleKeyDown}
              spellCheck={false}
              autoCapitalize="off"
              autoCorrect="off"
            />
          </div>
        </section>

        <div className="lower">
          <div className="console" aria-label="Consola de salida">
            <div className="panel__label">
              <span>Consola de salida</span>
            </div>
            <div className="console__body">
              {consoleLines.map((line, i) => (
                <div key={i} className={`console__line console__line--${line.type}`}>
                  {line.text}
                </div>
              ))}
              {isRunning && <div className="console__line console__line--info">…</div>}
            </div>
          </div>

          <div className="reports" aria-label="Reportes" ref={reportsRef}>
            <div className="reports__tabs">
              <button
                type="button"
                className={`tab ${reportTab === 'errors' ? 'tab--active' : ''}`}
                onClick={() => setReportTab('errors')}
              >
                Errores
                {result.errors.length > 0 && <span className="badge badge--danger">{result.errors.length}</span>}
              </button>
              <button
                type="button"
                className={`tab ${reportTab === 'symbols' ? 'tab--active' : ''}`}
                onClick={() => setReportTab('symbols')}
              >
                Tabla de simbolos
                {result.symbols.length > 0 && <span className="badge">{result.symbols.length}</span>}
              </button>
              <button
                type="button"
                className={`tab ${reportTab === 'ast' ? 'tab--active' : ''}`}
                onClick={() => setReportTab('ast')}
              >
                AST
              </button>
            </div>

            <div className="reports__body">
              {reportTab === 'errors' && (
                result.errors.length === 0 ? (
                  <EmptyState text="No se encontraron errores, el programa compilo con exito." />
                ) : (
                  <table className="report-table">
                    <thead>
                      <tr><th>No</th><th>Tipo</th><th>Descripcion</th><th>Linea</th><th>Columna</th></tr>
                    </thead>
                    <tbody>
                      {result.errors.map((e, i) => (
                        <tr key={i}>
                          <td>{i + 1}</td>
                          <td><span className={`tag tag--${e.tipo?.toLowerCase()}`}>{e.tipo || 'Error'}</span></td>
                          <td>{e.mensaje || e.descripcion || e}</td>
                          <td>{e.linea || '—'}</td>
                          <td>{e.columna || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
              )}

              {reportTab === 'symbols' && (
                result.symbols.length === 0 ? (
                  <EmptyState text="Aqui se mostrara la informacion de las variables y funciones registradas." />
                ) : (
                  <table className="report-table">
                    <thead>
                      <tr><th>No</th><th>Identificador</th><th>Categoria</th><th>Tipo</th><th>Ambito</th><th>Linea</th><th>Valor</th></tr>
                    </thead>
                    <tbody>
                      {result.symbols.map((s, i) => (
                        <tr key={i}>
                          <td>{s.no || i + 1}</td>
                          <td className="mono">{s.nombre}</td>
                          <td>{s.categoria}</td>
                          <td className="mono">{s.tipo}</td>
                          <td>{s.ambito}</td>
                          <td>{s.linea}</td>
                          <td className="mono">{s.valor ?? '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )
              )}

              {reportTab === 'ast' && (
                result.ast_image ? (
                  <div style={{ padding: '20px', textAlign: 'center' }}>
                    <img 
                      src={`data:image/png;base64,${result.ast_image}`} 
                      alt="Árbol de Sintaxis Abstracta"
                      style={{ maxWidth: '100%', height: 'auto' }}
                    />
                  </div>
                ) : result.ast.length > 0 ? (
                  <div className="ast-tree">
                    {result.ast.map((node, i) => (
                      <div key={i} className="ast-tree__node" style={{ paddingLeft: `${node.depth * 20}px` }}>
                        <span className="ast-tree__bullet" />
                        {node.label}
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState text="El arbol de sintaxis abstracta" />
                )
              )}
            </div>
          </div>
        </div>
      </main>

      <input
        type="file"
        accept=".ox,.rs,.txt"
        ref={fileInputRef}
        onChange={handleFileSelected}
        style={{ display: 'none' }}
      />
    </div>
  )
}

function EmptyState({ text }) {
  return <p className="empty-state">{text}</p>
}