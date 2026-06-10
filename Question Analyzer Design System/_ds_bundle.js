/* @ds-bundle: {"format":3,"namespace":"QuestionAnalyzerDesignSystem_03a921","components":[{"name":"Button","sourcePath":"components/Button/Button.jsx"},{"name":"Card","sourcePath":"components/Card/Card.jsx"},{"name":"FileDropzone","sourcePath":"components/FileDropzone/FileDropzone.jsx"},{"name":"MetricTile","sourcePath":"components/MetricTile/MetricTile.jsx"},{"name":"QuestionGroup","sourcePath":"components/QuestionGroup/QuestionGroup.jsx"},{"name":"Slider","sourcePath":"components/Slider/Slider.jsx"},{"name":"Tag","sourcePath":"components/Tag/Tag.jsx"}],"sourceHashes":{"components/Button/Button.jsx":"33bd71e0fcdb","components/Card/Card.jsx":"b1e7fb9aff3d","components/FileDropzone/FileDropzone.jsx":"76c7a5fe2c66","components/MetricTile/MetricTile.jsx":"cfdd0ef9f91b","components/QuestionGroup/QuestionGroup.jsx":"3f8ab9213ace","components/Slider/Slider.jsx":"f6c12e0dbb3a","components/Tag/Tag.jsx":"7c89450bc3ad","ui_kits/analyzer/App.jsx":"22749bcd0b29","ui_kits/analyzer/AppHeader.jsx":"0f2378c0e031","ui_kits/analyzer/DashboardView.jsx":"2a83ce8b6c1c","ui_kits/analyzer/Icon.jsx":"2e52c87a9663","ui_kits/analyzer/Modals.jsx":"de96e8a4eb7a","ui_kits/analyzer/RankedRow.jsx":"986e13a0186b","ui_kits/analyzer/WeekView.jsx":"7639602cb1c1","ui_kits/analyzer/anim.jsx":"5b19d067c7e7","ui_kits/analyzer/app-data.jsx":"6578715dacf9","ui_kits/analyzer/explore/WirDigest.jsx":"0ec6cc7eafaf","ui_kits/analyzer/explore/WirPulse.jsx":"39150e70e8f9","ui_kits/analyzer/explore/WirScorecard.jsx":"70fa51b83c8d","ui_kits/analyzer/explore/design-canvas.jsx":"bd8746af6e58","ui_kits/analyzer/explore/week-data.jsx":"bd4147185a14","ui_kits/analyzer/explore/wir-shared.jsx":"f69a92b00356"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.QuestionAnalyzerDesignSystem_03a921 = window.QuestionAnalyzerDesignSystem_03a921 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/Button/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Button — IBM Carbon-style action trigger.
 * Sharp corners, asymmetric padding when an icon is present (Carbon hallmark:
 * label left, icon pinned right). Variants: primary, secondary, tertiary, ghost, danger.
 */
function Button({
  children,
  variant = 'primary',
  size = 'lg',
  icon = null,
  fullWidth = false,
  disabled = false,
  onClick,
  type = 'button',
  ...rest
}) {
  const heights = {
    sm: '2rem',
    md: '2.5rem',
    lg: '3rem'
  };
  const palettes = {
    primary: {
      bg: 'var(--button-primary)',
      bgHover: 'var(--button-primary-hover)',
      color: 'var(--text-on-color)',
      border: 'transparent'
    },
    secondary: {
      bg: 'var(--button-secondary)',
      bgHover: 'var(--button-secondary-hover)',
      color: 'var(--text-on-color)',
      border: 'transparent'
    },
    tertiary: {
      bg: 'transparent',
      bgHover: 'var(--blue-60)',
      color: 'var(--blue-60)',
      border: 'var(--blue-60)',
      colorHover: 'var(--text-on-color)'
    },
    ghost: {
      bg: 'transparent',
      bgHover: 'var(--layer-hover)',
      color: 'var(--blue-60)',
      border: 'transparent'
    },
    danger: {
      bg: 'var(--button-danger)',
      bgHover: 'var(--button-danger-hover)',
      color: 'var(--text-on-color)',
      border: 'transparent'
    }
  };
  const p = palettes[variant] || palettes.primary;
  const [hover, setHover] = React.useState(false);
  const hasIcon = !!icon;
  const style = {
    appearance: 'none',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: hasIcon && !fullWidth ? 'space-between' : 'center',
    gap: 'var(--spacing-05)',
    width: fullWidth ? '100%' : 'auto',
    minWidth: variant === 'ghost' ? 0 : '6rem',
    height: heights[size] || heights.lg,
    // Carbon asymmetric padding: roomy right when icon sits at the edge
    padding: hasIcon ? '0 var(--spacing-05) 0 var(--spacing-05)' : '0 var(--spacing-07) 0 var(--spacing-05)',
    paddingRight: hasIcon && !fullWidth ? 'var(--spacing-09)' : undefined,
    fontFamily: 'var(--font-sans)',
    fontSize: 'var(--type-body-01)',
    fontWeight: 'var(--weight-regular)',
    lineHeight: 1,
    letterSpacing: '0.01em',
    textAlign: 'left',
    cursor: disabled ? 'not-allowed' : 'pointer',
    border: `1px solid ${p.border}`,
    borderRadius: 'var(--radius-none)',
    background: disabled ? 'var(--gray-20)' : hover ? p.bgHover : p.bg,
    color: disabled ? 'var(--text-disabled)' : hover && p.colorHover ? p.colorHover : p.color,
    transition: 'background var(--duration-base) var(--ease-productive), color var(--duration-base) var(--ease-productive)',
    outline: 'none',
    position: 'relative'
  };
  return /*#__PURE__*/React.createElement("button", _extends({
    type: type,
    style: style,
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    onFocus: e => {
      e.target.style.boxShadow = 'var(--focus-ring-inset)';
    },
    onBlur: e => {
      e.target.style.boxShadow = 'none';
    }
  }, rest), /*#__PURE__*/React.createElement("span", null, children), icon ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      flex: '0 0 auto'
    }
  }, icon) : null);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Button/Button.jsx", error: String((e && e.message) || e) }); }

// components/Card/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Card — Carbon layered surface. Sharp corners, 1px subtle border,
 * optional left accent bar and hover elevation.
 */
function Card({
  children,
  padding = 'var(--spacing-06)',
  accent = null,
  interactive = false,
  selected = false,
  onClick,
  style = {},
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const base = {
    position: 'relative',
    background: 'var(--layer-02)',
    border: `1px solid ${selected ? 'var(--blue-60)' : 'var(--border-subtle)'}`,
    borderRadius: 'var(--radius-none)',
    padding,
    boxShadow: interactive && hover ? 'var(--shadow-md)' : 'none',
    cursor: interactive ? 'pointer' : 'default',
    transition: 'box-shadow var(--duration-base) var(--ease-productive), border-color var(--duration-base) var(--ease-productive)',
    ...style
  };
  return /*#__PURE__*/React.createElement("div", _extends({
    style: base,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false)
  }, rest), accent ? /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 0,
      top: 0,
      bottom: 0,
      width: 3,
      background: accent
    }
  }) : null, children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Card/Card.jsx", error: String((e && e.message) || e) }); }

// components/FileDropzone/FileDropzone.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * FileDropzone — Carbon file-uploader. Dashed field, drag-active state,
 * supported-format helper text, and a selected-file chip.
 */
function FileDropzone({
  accept = '.txt,.json,.csv',
  hint = 'TXT, JSON or CSV up to 200MB',
  title = 'Drag a Slack export here or click to browse',
  fileName = null,
  onFile,
  onClear,
  ...rest
}) {
  const [drag, setDrag] = React.useState(false);
  const inputRef = React.useRef(null);
  const pick = () => inputRef.current && inputRef.current.click();
  const handle = file => {
    if (file && onFile) onFile(file);
  };
  if (fileName) {
    return /*#__PURE__*/React.createElement("div", _extends({
      style: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--spacing-04)',
        padding: 'var(--spacing-04) var(--spacing-05)',
        background: 'var(--layer-02)',
        border: '1px solid var(--border-subtle)',
        borderLeft: '3px solid var(--green-60)'
      }
    }, rest), /*#__PURE__*/React.createElement("span", {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--spacing-04)',
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("svg", {
      width: "20",
      height: "20",
      viewBox: "0 0 20 20",
      fill: "none",
      style: {
        flex: '0 0 auto'
      }
    }, /*#__PURE__*/React.createElement("path", {
      d: "M11 2H5a1 1 0 00-1 1v14a1 1 0 001 1h10a1 1 0 001-1V7l-5-5z",
      stroke: "var(--text-secondary)",
      strokeWidth: "1.25"
    }), /*#__PURE__*/React.createElement("path", {
      d: "M11 2v5h5",
      stroke: "var(--text-secondary)",
      strokeWidth: "1.25"
    })), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-sans)',
        fontSize: 'var(--type-body-01)',
        color: 'var(--text-primary)',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap'
      }
    }, fileName)), /*#__PURE__*/React.createElement("button", {
      type: "button",
      onClick: onClear,
      "aria-label": "Remove file",
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: 24,
        height: 24,
        border: 'none',
        background: 'transparent',
        color: 'var(--text-secondary)',
        cursor: 'pointer'
      }
    }, /*#__PURE__*/React.createElement("svg", {
      width: "16",
      height: "16",
      viewBox: "0 0 16 16",
      fill: "none"
    }, /*#__PURE__*/React.createElement("path", {
      d: "M4 4l8 8M12 4l-8 8",
      stroke: "currentColor",
      strokeWidth: "1.25"
    }))));
  }
  return /*#__PURE__*/React.createElement("div", _extends({
    onClick: pick,
    onDragOver: e => {
      e.preventDefault();
      setDrag(true);
    },
    onDragLeave: () => setDrag(false),
    onDrop: e => {
      e.preventDefault();
      setDrag(false);
      handle(e.dataTransfer.files[0]);
    },
    style: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 'var(--spacing-04)',
      textAlign: 'center',
      padding: 'var(--spacing-09) var(--spacing-06)',
      background: drag ? 'var(--blue-10)' : 'var(--layer-01)',
      border: `1px dashed ${drag ? 'var(--blue-60)' : 'var(--border-strong)'}`,
      cursor: 'pointer',
      transition: 'background var(--duration-base) var(--ease-productive), border-color var(--duration-base) var(--ease-productive)'
    }
  }, rest), /*#__PURE__*/React.createElement("svg", {
    width: "28",
    height: "28",
    viewBox: "0 0 28 28",
    fill: "none"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M14 19V6M14 6l-5 5M14 6l5 5",
    stroke: drag ? 'var(--blue-60)' : 'var(--text-secondary)',
    strokeWidth: "1.4"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M5 19v2a1 1 0 001 1h16a1 1 0 001-1v-2",
    stroke: drag ? 'var(--blue-60)' : 'var(--text-secondary)',
    strokeWidth: "1.4"
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-body-02)',
      color: 'var(--text-primary)'
    }
  }, title), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-helper-01)',
      color: 'var(--text-helper)'
    }
  }, hint), /*#__PURE__*/React.createElement("input", {
    ref: inputRef,
    type: "file",
    accept: accept,
    style: {
      display: 'none'
    },
    onChange: e => handle(e.target.files[0])
  }));
}
Object.assign(__ds_scope, { FileDropzone });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/FileDropzone/FileDropzone.jsx", error: String((e && e.message) || e) }); }

// components/MetricTile/MetricTile.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * MetricTile — Carbon "big number" stat. Light-weight numeral, uppercase
 * label, optional delta. Used in the analysis summary row.
 */
function MetricTile({
  label,
  value,
  unit = null,
  delta = null,
  accent = 'var(--blue-60)',
  ...rest
}) {
  const positive = typeof delta === 'string' ? delta.trim().startsWith('+') : delta > 0;
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      background: 'var(--layer-02)',
      borderLeft: `3px solid ${accent}`,
      padding: 'var(--spacing-05) var(--spacing-06)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-03)',
      minWidth: 0
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-label-01)',
      letterSpacing: 'var(--tracking-caps)',
      textTransform: 'uppercase',
      color: 'var(--text-helper)',
      fontWeight: 'var(--weight-medium)'
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 'var(--spacing-03)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-heading-05)',
      fontWeight: 'var(--weight-light)',
      lineHeight: 1,
      color: 'var(--text-primary)',
      letterSpacing: 'var(--tracking-display)'
    }
  }, value), unit ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--type-body-01)',
      color: 'var(--text-secondary)'
    }
  }, unit) : null, delta != null ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-code-01)',
      color: positive ? 'var(--green-60)' : 'var(--red-60)'
    }
  }, delta) : null));
}
Object.assign(__ds_scope, { MetricTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/MetricTile/MetricTile.jsx", error: String((e && e.message) || e) }); }

// components/QuestionGroup/QuestionGroup.jsx
try { (() => {
/**
 * QuestionGroup — the analyzer's hero row. A ranked, expandable group of
 * semantically-similar questions: rank numeral, representative question,
 * frequency heat-bar, keyword tags, similarity, and the underlying questions.
 */
function QuestionGroup({
  rank,
  question,
  count,
  maxCount = count,
  similarity = null,
  keywords = [],
  questions = [],
  defaultOpen = false
}) {
  const [open, setOpen] = React.useState(defaultOpen);
  const [hover, setHover] = React.useState(false);
  const pct = Math.max(6, Math.round(count / Math.max(1, maxCount) * 100));
  const heat = rank === 1 ? 'var(--blue-60)' : rank === 2 ? 'var(--blue-50)' : rank === 3 ? 'var(--blue-40)' : 'var(--gray-40)';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--layer-02)',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => setOpen(!open),
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      width: '100%',
      display: 'grid',
      gridTemplateColumns: 'auto 1fr auto auto',
      alignItems: 'center',
      gap: 'var(--spacing-05)',
      padding: 'var(--spacing-05) var(--spacing-06)',
      background: hover ? 'var(--layer-hover)' : 'transparent',
      border: 'none',
      borderLeft: `3px solid ${open ? heat : 'transparent'}`,
      textAlign: 'left',
      cursor: 'pointer',
      transition: 'background var(--duration-base) var(--ease-productive)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-heading-03)',
      fontWeight: 'var(--weight-regular)',
      color: heat,
      width: '2.25rem',
      textAlign: 'right',
      fontVariantNumeric: 'tabular-nums'
    }
  }, String(rank).padStart(2, '0')), /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0,
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-03)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-body-02)',
      color: 'var(--text-primary)',
      lineHeight: 'var(--lh-snug)',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: open ? 'normal' : 'nowrap'
    }
  }, question), keywords.length ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--spacing-02)'
    }
  }, keywords.slice(0, 5).map((k, i) => /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: '11px',
      color: 'var(--text-helper)',
      background: 'var(--gray-10)',
      padding: '1px 6px',
      borderRadius: 'var(--radius-sm)'
    }
  }, k))) : null), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--spacing-04)',
      width: '11rem'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      height: 6,
      background: 'var(--gray-10)',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 0,
      top: 0,
      bottom: 0,
      width: `${pct}%`,
      background: heat
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-body-01)',
      fontWeight: 'var(--weight-medium)',
      color: 'var(--text-primary)',
      fontVariantNumeric: 'tabular-nums',
      width: '2.5rem',
      textAlign: 'right'
    }
  }, count, "\xD7")), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      color: 'var(--text-secondary)',
      transform: open ? 'rotate(180deg)' : 'none',
      transition: 'transform var(--duration-base) var(--ease-productive)'
    }
  }, /*#__PURE__*/React.createElement("svg", {
    width: "16",
    height: "16",
    viewBox: "0 0 16 16",
    fill: "none"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M4 6l4 4 4-4",
    stroke: "currentColor",
    strokeWidth: "1.25"
  })))), open ? /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 var(--spacing-06) var(--spacing-06) calc(var(--spacing-06) + 2.25rem + var(--spacing-05))'
    }
  }, similarity != null ? /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-label-01)',
      color: 'var(--text-helper)',
      marginBottom: 'var(--spacing-04)'
    }
  }, "Avg. similarity ", /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-secondary)',
      fontFamily: 'var(--font-mono)'
    }
  }, similarity), " \xB7 ", questions.length, " occurrences") : null, /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0,
      borderLeft: '1px solid var(--border-subtle)'
    }
  }, questions.map((q, i) => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 'var(--spacing-05)',
      padding: 'var(--spacing-03) var(--spacing-05)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-body-01)',
      color: 'var(--text-secondary)',
      lineHeight: 'var(--lh-normal)'
    }
  }, q.text), q.date ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-code-01)',
      color: 'var(--text-placeholder)',
      whiteSpace: 'nowrap'
    }
  }, q.date) : null)))) : null);
}
Object.assign(__ds_scope, { QuestionGroup });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/QuestionGroup/QuestionGroup.jsx", error: String((e && e.message) || e) }); }

// components/Slider/Slider.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Slider — Carbon range control. Thin rail, filled progress, round thumb,
 * and a live numeric readout. Used for the similarity threshold.
 */
function Slider({
  value,
  min = 0,
  max = 100,
  step = 1,
  onChange,
  label = null,
  format = v => v,
  disabled = false,
  ...rest
}) {
  const pct = (value - min) / (max - min) * 100;
  const [active, setActive] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", _extends({
    style: {
      width: '100%'
    }
  }, rest), label ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      marginBottom: 'var(--spacing-04)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontSize: 'var(--type-label-01)',
      color: 'var(--text-secondary)',
      letterSpacing: 'var(--tracking-label)'
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-body-01)',
      color: 'var(--text-primary)',
      fontWeight: 'var(--weight-medium)'
    }
  }, format(value))) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 'var(--spacing-04)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-code-01)',
      color: 'var(--text-helper)'
    }
  }, format(min)), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      flex: 1,
      height: 16,
      display: 'flex',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      left: 0,
      right: 0,
      height: 2,
      background: 'var(--gray-30)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      left: 0,
      width: `${pct}%`,
      height: 2,
      background: disabled ? 'var(--gray-40)' : 'var(--gray-100)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      left: `${pct}%`,
      transform: 'translateX(-50%)',
      width: 14,
      height: 14,
      borderRadius: '50%',
      background: disabled ? 'var(--gray-40)' : 'var(--gray-100)',
      boxShadow: active ? '0 0 0 3px var(--blue-20)' : 'none',
      transition: 'box-shadow var(--duration-fast) var(--ease-productive)',
      pointerEvents: 'none'
    }
  }), /*#__PURE__*/React.createElement("input", {
    type: "range",
    min: min,
    max: max,
    step: step,
    value: value,
    disabled: disabled,
    onChange: e => onChange && onChange(Number(e.target.value)),
    onMouseDown: () => setActive(true),
    onMouseUp: () => setActive(false),
    onFocus: () => setActive(true),
    onBlur: () => setActive(false),
    style: {
      position: 'absolute',
      left: 0,
      right: 0,
      width: '100%',
      margin: 0,
      height: 16,
      opacity: 0,
      cursor: disabled ? 'not-allowed' : 'pointer'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 'var(--type-code-01)',
      color: 'var(--text-helper)'
    }
  }, format(max))));
}
Object.assign(__ds_scope, { Slider });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Slider/Slider.jsx", error: String((e && e.message) || e) }); }

// components/Tag/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Tag — Carbon pill tag for keywords, categories, and counts.
 * Color pairs follow Carbon (soft fill + deep text). Optional dismiss / dot.
 */
function Tag({
  children,
  color = 'gray',
  size = 'md',
  outline = false,
  dot = false,
  onDismiss = null,
  ...rest
}) {
  const pairs = {
    gray: {
      bg: 'var(--gray-20)',
      fg: 'var(--gray-100)',
      line: 'var(--gray-50)'
    },
    blue: {
      bg: 'var(--blue-20)',
      fg: 'var(--blue-80)',
      line: 'var(--blue-60)'
    },
    green: {
      bg: '#a7f0ba',
      fg: '#044317',
      line: 'var(--green-60)'
    },
    red: {
      bg: '#ffd7d9',
      fg: '#750e13',
      line: 'var(--red-60)'
    },
    purple: {
      bg: '#e8daff',
      fg: '#491d8b',
      line: 'var(--purple-60)'
    },
    teal: {
      bg: '#9ef0f0',
      fg: '#004144',
      line: 'var(--teal-60)'
    },
    magenta: {
      bg: '#ffd6e8',
      fg: '#740937',
      line: 'var(--magenta-60)'
    },
    cyan: {
      bg: '#bae6ff',
      fg: '#00539a',
      line: 'var(--cyan-50)'
    }
  };
  const p = pairs[color] || pairs.gray;
  const heights = {
    sm: '1.125rem',
    md: '1.5rem'
  };
  const style = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 'var(--spacing-02)',
    height: heights[size] || heights.md,
    padding: size === 'sm' ? '0 var(--spacing-03)' : '0 var(--spacing-04)',
    borderRadius: 'var(--radius-pill)',
    fontFamily: 'var(--font-sans)',
    fontSize: 'var(--type-label-01)',
    fontWeight: 'var(--weight-regular)',
    lineHeight: 1,
    whiteSpace: 'nowrap',
    background: outline ? 'transparent' : p.bg,
    color: outline ? p.fg : p.fg,
    border: outline ? `1px solid ${p.line}` : '1px solid transparent'
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: style
  }, rest), dot ? /*#__PURE__*/React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: '50%',
      background: p.line,
      flex: '0 0 auto'
    }
  }) : null, /*#__PURE__*/React.createElement("span", null, children), onDismiss ? /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: onDismiss,
    "aria-label": "Dismiss",
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: 16,
      height: 16,
      marginRight: -4,
      padding: 0,
      border: 'none',
      background: 'transparent',
      color: p.fg,
      cursor: 'pointer',
      borderRadius: '50%'
    }
  }, /*#__PURE__*/React.createElement("svg", {
    width: "12",
    height: "12",
    viewBox: "0 0 16 16",
    fill: "none"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M4 4l8 8M12 4l-8 8",
    stroke: "currentColor",
    strokeWidth: "1.25"
  }))) : null);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Tag/Tag.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/App.jsx
try { (() => {
// Question Analyzer — consolidated app.
function App() {
  const [view, setView] = React.useState('dashboard');
  const [uploadOpen, setUploadOpen] = React.useState(false);
  const [signInOpen, setSignInOpen] = React.useState(false);
  const [account, setAccount] = React.useState(null);
  const connect = email => {
    const base = email.split('@')[0].replace(/[^a-z]/gi, '');
    const initials = (base.slice(0, 2) || 'me').toUpperCase();
    setAccount({
      email,
      initials
    });
    setSignInOpen(false);
  };
  const disconnect = () => {
    setAccount(null);
    setSignInOpen(false);
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement(AppHeader, {
    view: view,
    setView: setView,
    onUpload: () => setUploadOpen(true),
    account: account,
    onAvatar: () => setSignInOpen(true),
    onManage: () => setSignInOpen(true)
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minHeight: 0,
      overflowY: 'auto',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement("div", {
    key: view,
    className: "qa-view"
  }, view === 'dashboard' ? /*#__PURE__*/React.createElement(DashboardView, null) : /*#__PURE__*/React.createElement(WeekView, null))), /*#__PURE__*/React.createElement(UploadModal, {
    open: uploadOpen,
    onClose: () => setUploadOpen(false),
    onImported: () => {
      setUploadOpen(false);
      setView('dashboard');
    }
  }), /*#__PURE__*/React.createElement(SignInModal, {
    open: signInOpen,
    onClose: () => setSignInOpen(false),
    account: account,
    onConnect: connect,
    onDisconnect: disconnect
  }));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(App, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/AppHeader.jsx
try { (() => {
// App header: brand, animated Dashboard | Week in Review toggle,
// Upload transcript, and the account / sign-in avatar.
function AppHeader({
  view,
  setView,
  onUpload,
  account,
  onAvatar,
  onManage
}) {
  const segs = [{
    key: 'dashboard',
    label: 'Dashboard'
  }, {
    key: 'week',
    label: 'Week in Review'
  }];
  const activeIdx = segs.findIndex(s => s.key === view);
  const seg = (s, i) => ({
    position: 'relative',
    zIndex: 1,
    height: 32,
    padding: '0 18px',
    display: 'inline-flex',
    alignItems: 'center',
    whiteSpace: 'nowrap',
    fontFamily: 'var(--font-sans)',
    fontSize: 13,
    cursor: 'pointer',
    border: 'none',
    background: 'transparent',
    color: view === s.key ? '#fff' : 'var(--gray-30)',
    transition: 'color var(--duration-moderate) var(--ease-productive)'
  });
  return /*#__PURE__*/React.createElement("header", {
    style: {
      height: 48,
      background: 'var(--gray-100)',
      color: '#fff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 16px',
      flex: '0 0 auto',
      zIndex: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'relative',
      display: 'inline-flex',
      border: '1px solid var(--gray-80)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      top: 0,
      bottom: 0,
      left: 0,
      width: `${100 / segs.length}%`,
      background: 'var(--blue-60)',
      transform: `translateX(${activeIdx * 100}%)`,
      transition: 'transform var(--duration-moderate) var(--ease-productive)',
      zIndex: 0
    }
  }), segs.map((s, i) => /*#__PURE__*/React.createElement("button", {
    key: s.key,
    style: seg(s, i),
    onClick: () => setView(s.key)
  }, s.label)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("button", {
    onClick: onUpload,
    style: {
      height: 32,
      padding: '0 14px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8,
      background: 'transparent',
      color: '#fff',
      border: '1px solid var(--gray-70)',
      fontFamily: 'var(--font-sans)',
      fontSize: 13,
      cursor: 'pointer',
      whiteSpace: 'nowrap',
      transition: 'background var(--duration-base) var(--ease-productive), border-color var(--duration-base)'
    },
    onMouseEnter: e => {
      e.currentTarget.style.background = 'var(--gray-80)';
      e.currentTarget.style.borderColor = 'var(--gray-50)';
    },
    onMouseLeave: e => {
      e.currentTarget.style.background = 'transparent';
      e.currentTarget.style.borderColor = 'var(--gray-70)';
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "upload",
    size: 15
  }), " Upload transcript"), account ? /*#__PURE__*/React.createElement("button", {
    onClick: onManage,
    title: account.email,
    style: {
      height: 32,
      padding: '0 6px 0 10px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8,
      background: 'var(--gray-90)',
      color: '#fff',
      border: '1px solid var(--gray-70)',
      cursor: 'pointer',
      fontFamily: 'var(--font-sans)',
      fontSize: 12.5
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 5,
      color: 'var(--green-50)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: '50%',
      background: 'var(--green-50)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      maxWidth: 150,
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap'
    }
  }, account.email), /*#__PURE__*/React.createElement("span", {
    style: {
      width: 24,
      height: 24,
      borderRadius: '50%',
      background: 'var(--blue-60)',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 11,
      fontWeight: 600
    }
  }, account.initials)) : /*#__PURE__*/React.createElement("button", {
    onClick: onAvatar,
    style: {
      width: 32,
      height: 32,
      borderRadius: '50%',
      background: 'var(--gray-80)',
      border: '1px solid var(--gray-60)',
      color: 'var(--gray-30)',
      cursor: 'pointer',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'background var(--duration-base) var(--ease-productive)'
    },
    onMouseEnter: e => {
      e.currentTarget.style.background = 'var(--blue-60)';
      e.currentTarget.style.color = '#fff';
    },
    onMouseLeave: e => {
      e.currentTarget.style.background = 'var(--gray-80)';
      e.currentTarget.style.color = 'var(--gray-30)';
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "user",
    size: 16
  }))));
}
window.AppHeader = AppHeader;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/AppHeader.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/DashboardView.jsx
try { (() => {
// Overall dashboard — common questions, ranked by occurrences (all-time).
function DashboardView() {
  const d = window.DASHBOARD_DATA;
  const [query, setQuery] = React.useState('');
  const max = d.groups[0].count;
  const groups = d.groups.filter(g => g.question.toLowerCase().includes(query.toLowerCase()) || g.keywords.join(' ').includes(query.toLowerCase()) || g.topic.toLowerCase().includes(query.toLowerCase()));
  const stat = (label, value, accent) => /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      fontWeight: 500
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 34,
      fontWeight: 300,
      letterSpacing: '-.02em',
      lineHeight: 1,
      color: accent || 'var(--text-primary)',
      fontVariantNumeric: 'tabular-nums'
    }
  }, /*#__PURE__*/React.createElement(CountUp, {
    to: value
  })));
  const search = {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    height: 40,
    padding: '0 14px',
    background: 'var(--field)',
    borderBottom: '1px solid var(--border-strong)',
    width: 300,
    maxWidth: '40vw'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 1000,
      margin: '0 auto',
      padding: '44px 40px 80px',
      width: '100%'
    }
  }, /*#__PURE__*/React.createElement(Reveal, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      gap: 24,
      flexWrap: 'wrap',
      marginBottom: 30
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontSize: 32,
      fontWeight: 300,
      letterSpacing: '-.02em',
      margin: '0 0 6px'
    }
  }, "Most-asked questions"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 14,
      color: 'var(--text-secondary)'
    }
  }, "All-time across your monitored Slack channels \xB7 ranked by occurrences")), /*#__PURE__*/React.createElement("div", {
    style: search
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "search",
    size: 16,
    color: "var(--text-helper)"
  }), /*#__PURE__*/React.createElement("input", {
    value: query,
    onChange: e => setQuery(e.target.value),
    placeholder: "Filter questions or topics",
    style: {
      border: 'none',
      outline: 'none',
      background: 'transparent',
      fontFamily: 'var(--font-sans)',
      fontSize: 14,
      width: '100%',
      color: 'var(--text-primary)'
    }
  })))), /*#__PURE__*/React.createElement(Reveal, {
    delay: 90
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 56,
      padding: '22px 24px',
      background: 'var(--gray-10)',
      borderLeft: '3px solid var(--blue-60)',
      marginBottom: 32
    }
  }, stat('Questions logged', d.totalQuestions), stat('Distinct topics', d.totalGroups, 'var(--purple-60)'), stat('Answered', d.resolved, 'var(--teal-60)'), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
      justifyContent: 'center',
      marginLeft: 'auto',
      textAlign: 'right'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      fontWeight: 500
    }
  }, "Top topic"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 18,
      fontWeight: 600,
      color: 'var(--blue-70)'
    }
  }, d.topTopic)))), /*#__PURE__*/React.createElement(Reveal, {
    delay: 160
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: 'var(--text-helper)',
      fontWeight: 500
    }
  }, "Ranked \xB7 ", groups.length, " topics"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "arrow-down",
    size: 13
  }), " Most frequent first"))), /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-subtle)',
      borderBottom: 'none',
      background: '#fff'
    }
  }, groups.map((g, i) => /*#__PURE__*/React.createElement(RankedRow, {
    key: g.rank,
    rank: g.rank,
    index: i,
    question: g.question,
    count: g.count,
    maxCount: max,
    keywords: g.keywords,
    similarity: g.similarity,
    questions: g.questions,
    defaultOpen: i === 0 && !query
  })), groups.length === 0 ? /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 48,
      textAlign: 'center',
      color: 'var(--text-helper)',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, "No topics match \u201C", query, "\u201D.") : null));
}
window.DashboardView = DashboardView;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/DashboardView.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/Icon.jsx
try { (() => {
// Shared Lucide icon helper for the UI kit.
function Icon({
  name,
  size = 16,
  stroke = 2,
  color = 'currentColor',
  style = {}
}) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (ref.current && window.lucide) {
      ref.current.innerHTML = `<i data-lucide="${name}"></i>`;
      window.lucide.createIcons({
        attrs: {
          width: size,
          height: size,
          'stroke-width': stroke
        },
        nameAttr: 'data-lucide'
      });
    }
  }, [name, size, stroke]);
  return /*#__PURE__*/React.createElement("span", {
    ref: ref,
    style: {
      display: 'inline-flex',
      color,
      ...style
    }
  });
}
window.Icon = Icon;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/Icon.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/Modals.jsx
try { (() => {
// Modal shell + Upload-transcript and Connect-email flows.
function Modal({
  open,
  onClose,
  children,
  width = 480
}) {
  const [render, setRender] = React.useState(open);
  const [vis, setVis] = React.useState(false);
  React.useEffect(() => {
    if (open) {
      setRender(true);
      const r = requestAnimationFrame(() => setVis(true));
      return () => cancelAnimationFrame(r);
    }
    setVis(false);
    const id = setTimeout(() => setRender(false), 240);
    return () => clearTimeout(id);
  }, [open]);
  React.useEffect(() => {
    const onKey = e => {
      if (e.key === 'Escape') onClose();
    };
    if (open) window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);
  if (!render) return null;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'fixed',
      inset: 0,
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: onClose,
    style: {
      position: 'absolute',
      inset: 0,
      background: 'rgba(22,22,22,.55)',
      opacity: vis ? 1 : 0,
      transition: 'opacity 220ms var(--ease-entrance)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      width,
      maxWidth: '92vw',
      background: '#fff',
      boxShadow: 'var(--shadow-overlay)',
      opacity: vis ? 1 : 0,
      transform: vis ? 'none' : 'translateY(14px) scale(.97)',
      transition: 'opacity 240ms var(--ease-entrance), transform 240ms var(--ease-entrance)'
    }
  }, children));
}
function ModalHead({
  title,
  sub,
  onClose
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      padding: '22px 24px 16px'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 20,
      fontWeight: 400,
      letterSpacing: '-.01em'
    }
  }, title), sub ? /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13.5,
      color: 'var(--text-secondary)',
      marginTop: 6,
      lineHeight: 1.45,
      maxWidth: 380
    }
  }, sub) : null), /*#__PURE__*/React.createElement("button", {
    onClick: onClose,
    "aria-label": "Close",
    style: {
      width: 32,
      height: 32,
      border: 'none',
      background: 'transparent',
      cursor: 'pointer',
      color: 'var(--text-secondary)',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      flex: '0 0 auto'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "x",
    size: 18
  })));
}

// ---- Upload transcript ----
function UploadModal({
  open,
  onClose,
  onImported
}) {
  const {
    Button,
    FileDropzone
  } = window.QuestionAnalyzerDesignSystem_03a921;
  const [file, setFile] = React.useState(null);
  const [phase, setPhase] = React.useState('pick'); // pick | running | done
  const [progress, setProgress] = React.useState(0);
  const timer = React.useRef(null);
  React.useEffect(() => {
    if (!open) {
      setFile(null);
      setPhase('pick');
      setProgress(0);
      if (timer.current) clearInterval(timer.current);
    }
  }, [open]);
  const run = () => {
    setPhase('running');
    let p = 0;
    timer.current = setInterval(() => {
      p += 4;
      setProgress(p);
      if (p >= 100) {
        clearInterval(timer.current);
        setPhase('done');
      }
    }, 40);
  };
  const steps = ['Parsing transcript', 'Extracting questions', 'Embedding & grouping', 'Ranking by frequency'];
  const activeStep = Math.min(steps.length - 1, Math.floor(progress / 25));
  return /*#__PURE__*/React.createElement(Modal, {
    open: open,
    onClose: onClose,
    width: 520
  }, /*#__PURE__*/React.createElement(ModalHead, {
    title: "Upload transcript",
    sub: "Drop the JSON export your Slack bot produces. Questions are extracted, grouped, and merged into your dashboard.",
    onClose: onClose
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 24px 24px'
    }
  }, phase === 'pick' ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(FileDropzone, {
    fileName: file ? file.name : null,
    accept: ".json,.txt,.csv",
    title: "Drop a transcript export here or click to browse",
    hint: "JSON, TXT or CSV up to 200MB",
    onFile: f => setFile(f),
    onClear: () => setFile(null)
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 8,
      marginTop: 20
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    onClick: onClose
  }, "Cancel"), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    disabled: !file,
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "sparkles",
      size: 16
    }),
    onClick: run
  }, "Analyze"))) : null, phase === 'running' ? /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '8px 0 4px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      fontSize: 13,
      color: 'var(--text-secondary)',
      marginBottom: 8
    }
  }, /*#__PURE__*/React.createElement("span", null, steps[activeStep], "\u2026"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)'
    }
  }, progress, "%")), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 4,
      background: 'var(--gray-20)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      height: '100%',
      width: `${progress}%`,
      background: 'var(--blue-60)',
      transition: 'width 40ms linear'
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      marginTop: 18
    }
  }, steps.map((s, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      fontSize: 13,
      color: i <= activeStep ? 'var(--text-primary)' : 'var(--text-placeholder)',
      transition: 'color 200ms'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 16,
      height: 16,
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: i < activeStep ? 'var(--green-60)' : 'var(--blue-60)'
    }
  }, i < activeStep ? /*#__PURE__*/React.createElement(Icon, {
    name: "check",
    size: 14
  }) : i === activeStep ? /*#__PURE__*/React.createElement(Icon, {
    name: "loader",
    size: 14
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: '50%',
      background: 'var(--gray-30)'
    }
  })), s)))) : null, phase === 'done' ? /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: 'center',
      padding: '12px 0 4px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "qa-pop",
    style: {
      width: 56,
      height: 56,
      borderRadius: '50%',
      background: 'var(--green-60)',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      margin: '0 auto 16px'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "check",
    size: 28,
    color: "#fff"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 18,
      fontWeight: 400,
      marginBottom: 6
    }
  }, "Transcript analyzed"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13.5,
      color: 'var(--text-secondary)',
      marginBottom: 22
    }
  }, "Added ", /*#__PURE__*/React.createElement("b", null, "22 questions"), " across ", /*#__PURE__*/React.createElement("b", null, "8 topics"), ". Antivirus scanning is your most-asked this week."), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    fullWidth: true,
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "arrow-right",
      size: 16
    }),
    onClick: () => onImported && onImported()
  }, "View dashboard")) : null));
}

// ---- Connect email / manage ----
function SignInModal({
  open,
  onClose,
  account,
  onConnect,
  onDisconnect
}) {
  const {
    Button
  } = window.QuestionAnalyzerDesignSystem_03a921;
  const [email, setEmail] = React.useState('');
  const [focus, setFocus] = React.useState(false);
  React.useEffect(() => {
    if (!open) {
      setEmail('');
      setFocus(false);
    }
  }, [open]);
  const valid = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  if (account) {
    return /*#__PURE__*/React.createElement(Modal, {
      open: open,
      onClose: onClose,
      width: 440
    }, /*#__PURE__*/React.createElement(ModalHead, {
      title: "Weekly report",
      sub: null,
      onClose: onClose
    }), /*#__PURE__*/React.createElement("div", {
      style: {
        padding: '0 24px 24px'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '14px 16px',
        background: 'var(--gray-10)',
        borderLeft: '3px solid var(--green-60)',
        marginBottom: 18
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        width: 36,
        height: 36,
        borderRadius: '50%',
        background: 'var(--blue-60)',
        color: '#fff',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 600,
        fontSize: 13
      }
    }, account.initials), /*#__PURE__*/React.createElement("div", {
      style: {
        minWidth: 0
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 14,
        fontWeight: 500,
        overflow: 'hidden',
        textOverflow: 'ellipsis'
      }
    }, account.email), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12,
        color: 'var(--green-60)',
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5
      }
    }, /*#__PURE__*/React.createElement(Icon, {
      name: "check",
      size: 12
    }), " Weekly digest active"))), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 0',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: 13.5
      }
    }, /*#__PURE__*/React.createElement("span", null, "Next digest"), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-secondary)'
      }
    }, "Mon, Jun 15 \xB7 9:00")), /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        justifyContent: 'space-between',
        gap: 8,
        marginTop: 18
      }
    }, /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      icon: /*#__PURE__*/React.createElement(Icon, {
        name: "log-out",
        size: 16
      }),
      onClick: onDisconnect
    }, "Disconnect"), /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      onClick: onClose
    }, "Done"))));
  }
  return /*#__PURE__*/React.createElement(Modal, {
    open: open,
    onClose: onClose,
    width: 440
  }, /*#__PURE__*/React.createElement(ModalHead, {
    title: "Get your weekly report",
    sub: "Connect your email and we'll send a Week-in-Review digest \u2014 top questions and what's trending \u2014 every Monday morning.",
    onClose: onClose
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 24px 24px'
    }
  }, /*#__PURE__*/React.createElement("label", {
    style: {
      fontSize: 12,
      color: 'var(--text-secondary)',
      display: 'block',
      marginBottom: 6
    }
  }, "Work email"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      height: 44,
      padding: '0 14px',
      background: 'var(--field)',
      borderBottom: `2px solid ${focus ? 'var(--blue-60)' : 'var(--border-strong)'}`,
      transition: 'border-color var(--duration-base)'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "mail",
    size: 16,
    color: "var(--text-helper)"
  }), /*#__PURE__*/React.createElement("input", {
    type: "email",
    value: email,
    placeholder: "you@webmethods.io",
    autoFocus: true,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    onChange: e => setEmail(e.target.value),
    onKeyDown: e => {
      if (e.key === 'Enter' && valid) onConnect(email);
    },
    style: {
      border: 'none',
      outline: 'none',
      background: 'transparent',
      marginLeft: 10,
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      width: '100%',
      color: 'var(--text-primary)'
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      fontSize: 12,
      color: 'var(--text-helper)',
      margin: '14px 0 4px'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "calendar-clock",
    size: 14
  }), " Delivered Mondays \xB7 unsubscribe anytime"), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    fullWidth: true,
    disabled: !valid,
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "arrow-right",
      size: 16
    }),
    onClick: () => onConnect(email)
  }, "Connect email")));
}
Object.assign(window, {
  UploadModal,
  SignInModal
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/Modals.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/RankedRow.jsx
try { (() => {
// Animated, expandable ranked question row — shared by Dashboard & Week.
function RankedRow({
  rank,
  question,
  count,
  maxCount,
  keywords = [],
  movement = null,
  similarity = null,
  questions = null,
  index = 0,
  defaultOpen = false
}) {
  const [open, setOpen] = React.useState(defaultOpen);
  const [hover, setHover] = React.useState(false);
  const [shown, setShown] = React.useState(false);
  const bodyRef = React.useRef(null);
  const [bodyH, setBodyH] = React.useState(0);
  const expandable = !!(questions && questions.length);
  React.useEffect(() => {
    const id = setTimeout(() => setShown(true), 80 + index * 70);
    return () => clearTimeout(id);
  }, []);
  React.useEffect(() => {
    if (bodyRef.current) setBodyH(bodyRef.current.scrollHeight);
  }, [open, questions]);
  const heat = rank === 1 ? 'var(--blue-60)' : rank === 2 ? 'var(--blue-50)' : rank === 3 ? 'var(--blue-40)' : 'var(--gray-40)';
  const pct = Math.max(6, Math.round(count / Math.max(1, maxCount) * 100));
  return /*#__PURE__*/React.createElement("div", {
    style: {
      borderBottom: '1px solid var(--border-subtle)',
      background: hover ? 'var(--layer-hover)' : 'transparent',
      borderLeft: `3px solid ${open ? heat : 'transparent'}`,
      transition: 'background var(--duration-base) var(--ease-productive), border-left-color var(--duration-base), opacity 480ms var(--ease-entrance), transform 480ms var(--ease-entrance)',
      opacity: shown ? 1 : 0,
      transform: shown ? 'none' : 'translateY(10px)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: () => expandable && setOpen(!open),
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: 'grid',
      gridTemplateColumns: movement != null ? '30px 52px 1fr 168px 46px 22px' : '34px 1fr 168px 46px 22px',
      alignItems: 'center',
      gap: 16,
      padding: '15px 20px',
      cursor: expandable ? 'pointer' : 'default'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 18,
      color: heat,
      textAlign: 'right',
      fontVariantNumeric: 'tabular-nums'
    }
  }, String(rank).padStart(2, '0')), movement != null ? /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement(MovementBadge, {
    movement: movement
  })) : null, /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 15,
      color: 'var(--text-primary)',
      lineHeight: 1.3,
      whiteSpace: open ? 'normal' : 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, question), keywords.length ? /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 5,
      marginTop: 6
    }
  }, keywords.slice(0, 4).map((k, i) => /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 11,
      color: 'var(--text-helper)',
      background: 'var(--gray-10)',
      padding: '1px 7px'
    }
  }, k))) : null), /*#__PURE__*/React.createElement(Bar, {
    pct: pct,
    color: heat,
    height: 8,
    delay: index * 70,
    duration: 1000
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 15,
      fontWeight: 500,
      textAlign: 'right',
      color: 'var(--text-primary)',
      fontVariantNumeric: 'tabular-nums'
    }
  }, count, "\xD7"), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      justifyContent: 'center',
      color: 'var(--text-secondary)',
      opacity: expandable ? 1 : 0,
      transform: open ? 'rotate(180deg)' : 'none',
      transition: 'transform var(--duration-moderate) var(--ease-productive)'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "chevron-down",
    size: 16
  }))), expandable ? /*#__PURE__*/React.createElement("div", {
    style: {
      maxHeight: open ? bodyH : 0,
      overflow: 'hidden',
      transition: 'max-height var(--duration-slow) var(--ease-productive)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    ref: bodyRef,
    style: {
      padding: '0 20px 18px',
      marginLeft: movement != null ? 98 : 50
    }
  }, similarity ? /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)',
      marginBottom: 10
    }
  }, "Avg. similarity ", /*#__PURE__*/React.createElement("b", {
    style: {
      fontFamily: 'var(--font-mono)',
      color: 'var(--text-secondary)'
    }
  }, similarity), " \xB7 ", questions.length, " occurrences") : null, /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: 'none',
      margin: 0,
      padding: 0,
      borderLeft: '1px solid var(--border-subtle)'
    }
  }, questions.map((q, i) => /*#__PURE__*/React.createElement("li", {
    key: i,
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 16,
      padding: '8px 16px',
      opacity: open ? 1 : 0,
      transform: open ? 'none' : 'translateX(-6px)',
      transition: `opacity 360ms ${i * 70}ms var(--ease-entrance), transform 360ms ${i * 70}ms var(--ease-entrance)`
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13.5,
      color: 'var(--text-secondary)',
      lineHeight: 1.45
    }
  }, q.text), q.date ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 12,
      color: 'var(--text-placeholder)',
      whiteSpace: 'nowrap'
    }
  }, q.date) : null))))) : null);
}
window.RankedRow = RankedRow;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/RankedRow.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/WeekView.jsx
try { (() => {
// Week in Review — "Pulse": animated trend hero + ranked rows with movement.
function WeekView() {
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;
  const chev = {
    width: 32,
    height: 32,
    border: '1px solid var(--border-subtle)',
    background: '#fff',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    color: 'var(--text-secondary)'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: 1040,
      margin: '0 auto',
      padding: '36px 40px 80px',
      width: '100%'
    }
  }, /*#__PURE__*/React.createElement(Reveal, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 24
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      fontWeight: 500
    }
  }, "Week in review"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 22,
      fontWeight: 300,
      letterSpacing: '-.01em',
      marginTop: 4
    }
  }, d.weekLabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 6,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: chev
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "chevron-left",
    size: 16
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      ...chev,
      width: 'auto',
      padding: '0 12px',
      fontSize: 13,
      gap: 6,
      color: 'var(--text-secondary)'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "calendar",
    size: 14
  }), " This week"), /*#__PURE__*/React.createElement("span", {
    style: {
      ...chev,
      color: 'var(--text-placeholder)'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "chevron-right",
    size: 16
  }))))), /*#__PURE__*/React.createElement(Reveal, {
    delay: 80
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 320px',
      border: '1px solid var(--border-subtle)',
      marginBottom: 34,
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '22px 26px 14px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      fontWeight: 500,
      marginBottom: 4
    }
  }, "Weekly question volume"), /*#__PURE__*/React.createElement(AreaChart, {
    data: d.trend,
    labels: d.trendLabels,
    width: 560,
    height: 232
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '22px 26px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      gap: 20,
      borderLeft: '1px solid var(--border-subtle)',
      background: 'var(--gray-10)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      fontWeight: 500,
      marginBottom: 8
    }
  }, "Vs. last week"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "trending-up",
    size: 24,
    color: "var(--green-60)"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 42,
      fontWeight: 300,
      fontFamily: 'var(--font-mono)',
      lineHeight: 1,
      color: 'var(--green-60)'
    }
  }, "+", /*#__PURE__*/React.createElement(CountUp, {
    to: d.deltaPct,
    duration: 1300
  }), "%"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      fontSize: 12,
      color: 'var(--text-helper)',
      marginBottom: 5
    }
  }, /*#__PURE__*/React.createElement("span", null, "Last week"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      color: 'var(--text-secondary)'
    }
  }, d.totalLastWeek)), /*#__PURE__*/React.createElement(Bar, {
    pct: d.totalLastWeek / d.totalThisWeek * 100,
    color: "var(--gray-40)",
    bg: "var(--gray-20)",
    height: 8,
    delay: 220
  })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      fontSize: 12,
      color: 'var(--text-primary)',
      marginBottom: 5
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 500
    }
  }, "This week"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontWeight: 600
    }
  }, d.totalThisWeek)), /*#__PURE__*/React.createElement(Bar, {
    pct: 100,
    color: "var(--blue-60)",
    bg: "var(--gray-20)",
    height: 8,
    delay: 360
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 1,
      background: 'var(--border-subtle)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 30
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 26,
      fontWeight: 300,
      color: 'var(--text-primary)'
    }
  }, /*#__PURE__*/React.createElement(CountUp, {
    to: d.newQuestionTypes
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      marginTop: 2
    }
  }, "new topics")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 26,
      fontWeight: 300,
      color: 'var(--teal-60)'
    }
  }, /*#__PURE__*/React.createElement(CountUp, {
    to: d.answered
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--text-helper)',
      marginTop: 2
    }
  }, "answered")))))), /*#__PURE__*/React.createElement(Reveal, {
    delay: 160
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: 'var(--text-helper)',
      fontWeight: 500
    }
  }, "Questions this week, by frequency"))), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '2px solid var(--gray-100)',
      borderBottom: '1px solid var(--border-subtle)',
      background: '#fff'
    }
  }, d.groups.map((g, i) => /*#__PURE__*/React.createElement(RankedRow, {
    key: g.rank,
    rank: g.rank,
    index: i,
    question: g.question,
    count: g.count,
    maxCount: max,
    keywords: g.keywords,
    movement: g.movement
  }))));
}
window.WeekView = WeekView;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/WeekView.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/anim.jsx
try { (() => {
// ============================================================
// Animation toolkit — count-up, reveal, animated bars, and a
// polished SVG area chart with draw-on, gridlines, hover crosshair.
// ============================================================

// Count a number up on mount (easeOutCubic).
const QA_REDUCED = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
function useCountUp(target, opts = {}) {
  const {
    duration = 1100,
    decimals = 0,
    start = 0
  } = opts;
  const [val, setVal] = React.useState(QA_REDUCED ? target : start);
  React.useEffect(() => {
    if (QA_REDUCED) {
      setVal(target);
      return;
    }
    let raf;
    const t0 = performance.now();
    const tick = t => {
      const p = Math.min(1, (t - t0) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(start + (target - start) * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target]);
  return Number(val.toFixed(decimals)).toLocaleString();
}
function CountUp({
  to,
  decimals = 0,
  duration = 1100,
  prefix = '',
  suffix = ''
}) {
  const v = useCountUp(to, {
    decimals,
    duration
  });
  return /*#__PURE__*/React.createElement(React.Fragment, null, prefix, v, suffix);
}

// Fade + slide children in after `delay` ms.
function Reveal({
  children,
  delay = 0,
  y = 14,
  dur = 520,
  style = {}
}) {
  const [shown, setShown] = React.useState(QA_REDUCED);
  React.useEffect(() => {
    if (QA_REDUCED) return;
    const id = setTimeout(() => setShown(true), delay);
    return () => clearTimeout(id);
  }, []);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      opacity: shown ? 1 : 0,
      transform: shown ? 'none' : `translateY(${y}px)`,
      transition: `opacity ${dur}ms var(--ease-entrance), transform ${dur}ms var(--ease-entrance)`,
      ...style
    }
  }, children);
}

// Bar whose fill animates from 0 → pct%.
function Bar({
  pct,
  color,
  height = 8,
  bg = 'var(--gray-10)',
  delay = 0,
  duration = 900,
  radius = 0
}) {
  const [w, setW] = React.useState(QA_REDUCED ? pct : 0);
  React.useEffect(() => {
    if (QA_REDUCED) {
      setW(pct);
      return;
    }
    const id = setTimeout(() => setW(pct), delay + 40);
    return () => clearTimeout(id);
  }, [pct, delay]);
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      height,
      background: bg,
      position: 'relative',
      overflow: 'hidden',
      borderRadius: radius
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 0,
      top: 0,
      bottom: 0,
      width: `${w}%`,
      background: color,
      transition: `width ${duration}ms var(--ease-productive)`
    }
  }));
}

// Smooth Catmull-Rom → cubic bezier path.
function smoothPath(pts) {
  if (pts.length < 2) return '';
  let d = `M ${pts[0].x} ${pts[0].y}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i],
      p1 = pts[i],
      p2 = pts[i + 1],
      p3 = pts[i + 2] || p2;
    const c1x = p1.x + (p2.x - p0.x) / 6,
      c1y = p1.y + (p2.y - p0.y) / 6;
    const c2x = p2.x - (p3.x - p1.x) / 6,
      c2y = p2.y - (p3.y - p1.y) / 6;
    d += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)}, ${c2x.toFixed(1)} ${c2y.toFixed(1)}, ${p2.x} ${p2.y}`;
  }
  return d;
}

// Polished animated area chart.
function AreaChart({
  data,
  labels,
  width = 720,
  height = 240,
  accent = 'var(--blue-60)'
}) {
  const padL = 16,
    padR = 16,
    padT = 30,
    padB = 28;
  const plotW = width - padL - padR,
    plotH = height - padT - padB;
  const max = Math.max(...data) * 1.18,
    min = Math.min(...data) * 0.6;
  const x = i => padL + i / (data.length - 1) * plotW;
  const y = v => padT + plotH - (v - min) / (max - min) * plotH;
  const pts = data.map((v, i) => ({
    x: x(i),
    y: y(v)
  }));
  const line = smoothPath(pts);
  const area = `${line} L ${pts[pts.length - 1].x} ${padT + plotH} L ${pts[0].x} ${padT + plotH} Z`;
  const grid = [0, 0.25, 0.5, 0.75, 1].map(f => padT + plotH - f * plotH);
  const lineRef = React.useRef(null);
  const [drawn, setDrawn] = React.useState(QA_REDUCED);
  const [hover, setHover] = React.useState(null);
  const svgRef = React.useRef(null);
  React.useEffect(() => {
    const path = lineRef.current;
    if (!path) return;
    if (QA_REDUCED) {
      setDrawn(true);
      return;
    }
    const len = path.getTotalLength();
    path.style.transition = 'none';
    path.style.strokeDasharray = len;
    path.style.strokeDashoffset = len;
    // force reflow then animate
    path.getBoundingClientRect();
    requestAnimationFrame(() => {
      path.style.transition = 'stroke-dashoffset 1500ms var(--ease-productive)';
      path.style.strokeDashoffset = '0';
    });
    const id = setTimeout(() => setDrawn(true), 700);
    return () => clearTimeout(id);
  }, []);
  const onMove = e => {
    const r = svgRef.current.getBoundingClientRect();
    const mx = (e.clientX - r.left) / r.width * width;
    let idx = Math.round((mx - padL) / (plotW / (data.length - 1)));
    idx = Math.max(0, Math.min(data.length - 1, idx));
    setHover(idx);
  };
  const last = data.length - 1;
  const uid = React.useMemo(() => 'ac' + Math.random().toString(36).slice(2, 8), []);
  return /*#__PURE__*/React.createElement("svg", {
    ref: svgRef,
    viewBox: `0 0 ${width} ${height}`,
    style: {
      width: '100%',
      height: 'auto',
      display: 'block'
    },
    onMouseMove: onMove,
    onMouseLeave: () => setHover(null)
  }, /*#__PURE__*/React.createElement("defs", null, /*#__PURE__*/React.createElement("linearGradient", {
    id: uid,
    x1: "0",
    y1: "0",
    x2: "0",
    y2: "1"
  }, /*#__PURE__*/React.createElement("stop", {
    offset: "0%",
    stopColor: accent,
    stopOpacity: "0.20"
  }), /*#__PURE__*/React.createElement("stop", {
    offset: "100%",
    stopColor: accent,
    stopOpacity: "0"
  }))), grid.map((gy, i) => /*#__PURE__*/React.createElement("line", {
    key: i,
    x1: padL,
    y1: gy,
    x2: width - padR,
    y2: gy,
    stroke: "var(--gray-20)",
    strokeWidth: "1",
    strokeDasharray: i === grid.length - 1 ? '0' : '2 4',
    shapeRendering: "crispEdges"
  })), /*#__PURE__*/React.createElement("path", {
    d: area,
    fill: `url(#${uid})`,
    style: {
      opacity: drawn ? 1 : 0,
      transition: 'opacity 700ms var(--ease-entrance)'
    }
  }), /*#__PURE__*/React.createElement("path", {
    ref: lineRef,
    d: line,
    fill: "none",
    stroke: accent,
    strokeWidth: "2.5",
    strokeLinecap: "round",
    strokeLinejoin: "round",
    vectorEffect: "non-scaling-stroke"
  }), pts.map((p, i) => /*#__PURE__*/React.createElement("text", {
    key: i,
    x: p.x,
    y: p.y - 12,
    textAnchor: "middle",
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 11,
      fontWeight: i === last ? 600 : 400,
      fill: i === last ? accent : 'var(--text-placeholder)',
      opacity: drawn ? 1 : 0,
      transition: `opacity 400ms ${200 + i * 80}ms var(--ease-entrance)`
    }
  }, data[i])), pts.map((p, i) => /*#__PURE__*/React.createElement("text", {
    key: i,
    x: p.x,
    y: height - 8,
    textAnchor: "middle",
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 10,
      fill: i === last ? 'var(--text-secondary)' : 'var(--text-placeholder)'
    }
  }, labels[i])), hover != null ? /*#__PURE__*/React.createElement("g", null, /*#__PURE__*/React.createElement("line", {
    x1: pts[hover].x,
    y1: padT - 6,
    x2: pts[hover].x,
    y2: padT + plotH,
    stroke: "var(--gray-40)",
    strokeWidth: "1",
    strokeDasharray: "2 3"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: pts[hover].x,
    cy: pts[hover].y,
    r: "6",
    fill: "#fff",
    stroke: accent,
    strokeWidth: "2.5"
  })) : null, pts.map((p, i) => /*#__PURE__*/React.createElement("circle", {
    key: i,
    cx: p.x,
    cy: p.y,
    r: i === last ? 4.5 : 3,
    fill: i === last ? accent : '#fff',
    stroke: accent,
    strokeWidth: "2",
    style: {
      opacity: drawn ? 1 : 0,
      transition: `opacity 360ms ${300 + i * 70}ms var(--ease-entrance)`
    }
  })), drawn ? /*#__PURE__*/React.createElement("circle", {
    cx: pts[last].x,
    cy: pts[last].y,
    r: "4.5",
    fill: "none",
    stroke: accent,
    strokeWidth: "2",
    className: "qa-pulse"
  }) : null);
}

// ▲18% / ▼6% delta chip.
function DeltaBadge({
  value,
  size = 'md'
}) {
  const up = value >= 0;
  const big = size === 'lg';
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 4,
      color: up ? 'var(--green-60)' : 'var(--red-60)',
      fontFamily: 'var(--font-mono)',
      fontSize: big ? 18 : 13,
      fontWeight: 500
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: up ? 'trending-up' : 'trending-down',
    size: big ? 18 : 14
  }), up ? '+' : '', value, "%");
}

// NEW / ▲2 / ▼1 movement marker.
function MovementBadge({
  movement
}) {
  if (movement === 'new') {
    return /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        letterSpacing: '.5px',
        color: 'var(--blue-70)',
        background: 'var(--blue-20)',
        padding: '2px 7px'
      }
    }, "NEW");
  }
  if (typeof movement === 'number' && movement !== 0) {
    const up = movement > 0;
    return /*#__PURE__*/React.createElement("span", {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: 2,
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        color: up ? 'var(--green-60)' : 'var(--gray-50)'
      }
    }, /*#__PURE__*/React.createElement(Icon, {
      name: up ? 'arrow-up' : 'arrow-down',
      size: 12
    }), Math.abs(movement));
  }
  return /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 12,
      color: 'var(--text-placeholder)'
    }
  }, "\u2014");
}
Object.assign(window, {
  useCountUp,
  CountUp,
  Reveal,
  Bar,
  AreaChart,
  DeltaBadge,
  MovementBadge
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/anim.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/app-data.jsx
try { (() => {
// ============================================================
// App data — IBM webMethods MFT / IWHI question analytics.
// ============================================================

// Overall (all-time) dashboard: common questions ranked by occurrences.
window.DASHBOARD_DATA = {
  totalQuestions: 136,
  totalGroups: 10,
  resolved: 71,
  topTopic: 'Antivirus scanning',
  groups: [{
    rank: 1,
    count: 28,
    similarity: '92%',
    topic: 'Antivirus scanning',
    question: 'How do I configure virus scanning in MFT and handle scan failures?',
    keywords: ['mft', 'antivirus', 'quarantine', 'notification', 'post-processing'],
    questions: [{
      text: 'Copy Task to target failing: "Exception while scanning for virus".',
      date: 'Jun 5'
    }, {
      text: 'When a virus is detected, send an email notification to an admin?',
      date: 'Jun 5'
    }, {
      text: 'Post-processing scanner → move file to quarantine or approved + send mail?',
      date: 'Jun 2'
    }, {
      text: 'Can a post-processing script return a custom error to drive routing?',
      date: 'Jun 2'
    }]
  }, {
    rank: 2,
    count: 22,
    similarity: '90%',
    topic: 'Metering & usage',
    question: 'How can customers measure MFT transaction statistics without the metering server?',
    keywords: ['metering', 'transactions', 'usage', 'entitlements'],
    questions: [{
      text: 'Check own transaction stats (inbound/outbound counts, file sizes)?',
      date: 'May 30'
    }, {
      text: 'Estimate MFT transactions in the absence of a metering server?',
      date: 'Jun 2'
    }, {
      text: 'Does the Metering Agent ship pre-installed in the Capabilities Container images?',
      date: 'Jun 9'
    }]
  }, {
    rank: 3,
    count: 19,
    similarity: '89%',
    topic: 'Cloud storage connectivity',
    question: 'Azure Blob / cloud storage connectivity and token authorization',
    keywords: ['azure', 'sas-token', 'blob', 'authorization'],
    questions: [{
      text: 'Storage-account token works but Container-level SAS token fails authorization.',
      date: 'Jun 5'
    }, {
      text: 'Correct IPs, protocols, CRUD permissions — still a Container token auth failure.',
      date: 'Jun 5'
    }]
  }, {
    rank: 4,
    count: 17,
    similarity: '88%',
    topic: 'Scheduled Action APIs',
    question: 'Is there a REST API to trigger or deactivate Scheduled Actions?',
    keywords: ['rest-api', 'scheduled-actions', 'automation'],
    questions: [{
      text: 'REST API to deactivate a list of Scheduled and Post-Processing Actions?',
      date: 'Jun 5'
    }, {
      text: 'Trigger a file transfer via a REST API call instead of a schedule?',
      date: 'Jun 3'
    }]
  }, {
    rank: 5,
    count: 14,
    similarity: '86%',
    topic: 'UI errors after upgrade',
    question: 'Internal error / NullPointerException opening the MFT UI after a 12.x install',
    keywords: ['mft-ui', 'upgrade', 'nullpointer', 'error'],
    questions: [{
      text: 'Installed v12, cannot open MFT UI — MFTServiceException internal error.',
      date: 'Jun 3'
    }, {
      text: 'NullPointerException — Datastore.logger is null while fetching UI settings.',
      date: 'Jun 3'
    }]
  }, {
    rank: 6,
    count: 11,
    similarity: '84%',
    topic: 'Control-file triggers',
    question: 'Use a control (.ctrl) file to trigger transfer once the data file is ready',
    keywords: ['find-task', 'control-file', 'trigger'],
    questions: [{
      text: 'On finding {name}.ctrl, move {name}.dat to the destination?',
      date: 'Jun 5'
    }]
  }, {
    rank: 7,
    count: 9,
    similarity: '83%',
    topic: 'Monitoring & alerting',
    question: 'IWHI end-to-end monitoring & alerting best practices',
    keywords: ['iwhi', 'monitoring', 'alerting'],
    questions: [{
      text: 'Monitor a single app and alert on the first error — one group per product?',
      date: 'Jun 9'
    }]
  }, {
    rank: 8,
    count: 7,
    similarity: '81%',
    topic: 'Thread scaling',
    question: 'Avoiding thread exhaustion with thousands of scheduled actions',
    keywords: ['threads', 'scheduler', 'scaling'],
    questions: [{
      text: '8,600 scheduled actions on a 2-node cluster — how to avoid running out of threads?',
      date: 'Jun 5'
    }]
  }, {
    rank: 9,
    count: 5,
    similarity: '80%',
    topic: 'Certificates & key vaults',
    question: 'Integrate the Certificate store with an external key vault (e.g. HashiCorp)',
    keywords: ['certificate', 'key-vault', 'hashicorp'],
    questions: [{
      text: 'Can the platform Certificate store integrate with an external key vault?',
      date: 'Jun 3'
    }]
  }, {
    rank: 10,
    count: 4,
    similarity: '78%',
    topic: 'File merge',
    question: 'Merge content of multiple files via a Flow Service',
    keywords: ['flow-service', 'merge', 'files'],
    questions: [{
      text: 'Find file001.txt + file002.txt and merge via a Flow Service?',
      date: 'Jun 5'
    }]
  }]
};

// This-week view (Pulse). 6-week volume trend + ranked + movement.
window.WEEK_DATA = {
  weekLabel: 'Jun 2 – 8, 2026',
  totalThisWeek: 22,
  totalLastWeek: 18,
  deltaPct: +18,
  newQuestionTypes: 5,
  groupsThisWeek: 8,
  answered: 3,
  trend: [14, 12, 19, 16, 18, 22],
  trendLabels: ['May 5', 'May 12', 'May 19', 'May 26', 'Jun 1', 'Jun 8'],
  groups: [{
    rank: 1,
    count: 4,
    movement: 'new',
    topic: 'Antivirus scanning',
    question: 'How do I configure virus scanning in MFT and handle failures?',
    keywords: ['mft', 'antivirus', 'quarantine']
  }, {
    rank: 2,
    count: 3,
    movement: 'new',
    topic: 'Metering & usage',
    question: 'Measuring MFT transaction statistics without the metering server',
    keywords: ['metering', 'transactions', 'usage']
  }, {
    rank: 3,
    count: 2,
    movement: +2,
    topic: 'Scheduled Action APIs',
    question: 'Is there a REST API to trigger or deactivate Scheduled Actions?',
    keywords: ['rest-api', 'scheduled-actions']
  }, {
    rank: 4,
    count: 2,
    movement: 'new',
    topic: 'UI errors after upgrade',
    question: 'Internal error / NullPointerException opening MFT UI after 12.x install',
    keywords: ['mft-ui', 'upgrade', 'error']
  }, {
    rank: 5,
    count: 1,
    movement: -1,
    topic: 'Azure Blob auth',
    question: 'Azure Blob Container-level SAS token authorization failure',
    keywords: ['azure', 'sas-token']
  }, {
    rank: 6,
    count: 1,
    movement: 'new',
    topic: 'Control-file triggers',
    question: 'Use a control (.ctrl) file to trigger transfer when data is ready',
    keywords: ['find-task', 'control-file']
  }, {
    rank: 7,
    count: 1,
    movement: -3,
    topic: 'Monitoring & alerting',
    question: 'IWHI end-to-end monitoring & alerting best practices',
    keywords: ['iwhi', 'monitoring']
  }, {
    rank: 8,
    count: 1,
    movement: +1,
    topic: 'Thread scaling',
    question: 'Avoiding thread exhaustion with thousands of scheduled actions',
    keywords: ['threads', 'scheduler']
  }]
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/app-data.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/explore/WirDigest.jsx
try { (() => {
// OPTION A — "Briefing": editorial weekly digest, single column, email-ready.
function WirDigest() {
  const {
    Tag,
    Button
  } = DS_NS();
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;
  const wkline = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 28
  };
  const chev = {
    width: 32,
    height: 32,
    border: '1px solid var(--border-subtle)',
    background: '#fff',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    color: 'var(--text-secondary)'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement(AppShellHeader, {
    active: "week"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      overflow: 'hidden',
      padding: '40px 56px',
      maxWidth: 860,
      margin: '0 auto',
      width: '100%'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: wkline
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      textTransform: 'uppercase',
      letterSpacing: '.32px',
      color: 'var(--text-helper)',
      fontWeight: 500
    }
  }, "Weekly digest"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 14,
      fontFamily: 'var(--font-mono)',
      color: 'var(--text-secondary)',
      marginTop: 4
    }
  }, "Week of ", d.weekLabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: chev
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "chevron-left",
    size: 16
  })), /*#__PURE__*/React.createElement("span", {
    style: chev
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "chevron-right",
    size: 16
  })))), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontSize: 38,
      fontWeight: 300,
      letterSpacing: '-.02em',
      lineHeight: 1.15,
      margin: '0 0 20px',
      color: 'var(--text-primary)'
    }
  }, "Your channel asked ", /*#__PURE__*/React.createElement("b", {
    style: {
      fontWeight: 600
    }
  }, d.totalThisWeek, " questions"), " this week \u2014 up ", d.deltaPct, "% from last."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 40,
      marginBottom: 36,
      paddingBottom: 28,
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 32,
      fontWeight: 300
    }
  }, d.totalThisWeek), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)'
    }
  }, "questions logged")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 32,
      fontWeight: 300,
      color: 'var(--green-60)'
    }
  }, "+", d.deltaPct, "%")), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)'
    }
  }, "vs last week")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 32,
      fontWeight: 300
    }
  }, d.newQuestionTypes), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)'
    }
  }, "new question types"))), /*#__PURE__*/React.createElement("div", {
    style: {
      borderLeft: '3px solid var(--blue-60)',
      background: 'var(--blue-10)',
      padding: '18px 22px',
      marginBottom: 32
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      textTransform: 'uppercase',
      letterSpacing: '.32px',
      color: 'var(--blue-70)',
      fontWeight: 600,
      marginBottom: 8,
      display: 'flex',
      alignItems: 'center',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "sparkles",
    size: 14,
    color: "var(--blue-70)"
  }), " Spotlight \xB7 document this first"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 19,
      fontWeight: 400,
      lineHeight: 1.35,
      marginBottom: 8
    }
  }, d.groups[0].question), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      color: 'var(--text-secondary)'
    }
  }, "Asked ", /*#__PURE__*/React.createElement("b", null, d.groups[0].count, "\xD7"), " this week \u2014 your most-pressed topic. ", d.groups[0].keywords.slice(0, 3).join(', '), ".")), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 16,
      fontWeight: 600,
      marginBottom: 12
    }
  }, "The week, ranked"), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '1px solid var(--border-subtle)'
    }
  }, d.groups.map(g => /*#__PURE__*/React.createElement("div", {
    key: g.rank,
    style: {
      display: 'grid',
      gridTemplateColumns: '28px 1fr 120px 44px',
      alignItems: 'center',
      gap: 16,
      padding: '13px 0',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 15,
      color: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-50)',
      textAlign: 'right'
    }
  }, String(g.rank).padStart(2, '0')), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, g.question), g.movement === 'new' ? /*#__PURE__*/React.createElement(MovementBadge, {
    movement: "new"
  }) : null), /*#__PURE__*/React.createElement("span", {
    style: {
      height: 6,
      background: 'var(--gray-10)',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      inset: '0 auto 0 0',
      width: `${Math.max(8, g.count / max * 100)}%`,
      background: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-40)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 14,
      fontWeight: 500,
      textAlign: 'right'
    }
  }, g.count, "\xD7")))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 28,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "mail",
    size: 14
  }), " Delivered Mondays to sam.archer@webmethods.io"), /*#__PURE__*/React.createElement(Button, {
    variant: "tertiary",
    size: "md",
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "send",
      size: 16
    })
  }, "Post to Slack"))));
}
window.WirDigest = WirDigest;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/explore/WirDigest.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/explore/WirPulse.jsx
try { (() => {
// OPTION C — "Pulse": trend-led. Volume chart hero + delta, then ranked rows.
function WirPulse() {
  const {
    Button
  } = DS_NS();
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;
  const weeks = ['May 5', 'May 12', 'May 19', 'May 26', 'Jun 1', 'Jun 8'];
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement(AppShellHeader, {
    active: "week"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      overflow: 'hidden',
      padding: '32px 48px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontFamily: 'var(--font-mono)',
      color: 'var(--text-helper)'
    }
  }, "WEEK IN REVIEW \xB7 ", d.weekLabel), /*#__PURE__*/React.createElement(Button, {
    variant: "tertiary",
    size: "md",
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "send",
      size: 16
    })
  }, "Post to Slack")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 360px',
      gap: 0,
      border: '1px solid var(--border-subtle)',
      marginBottom: 28
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '24px 28px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      textTransform: 'uppercase',
      letterSpacing: '.32px',
      color: 'var(--text-helper)',
      fontWeight: 500,
      marginBottom: 16
    }
  }, "Weekly question volume \xB7 6 weeks"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      gap: 22
    }
  }, d.trend.map((v, i) => {
    const last = i === d.trend.length - 1;
    const h = Math.max(6, v / Math.max(...d.trend) * 120);
    return /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 8,
        flex: 1
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        fontWeight: last ? 600 : 400,
        color: last ? 'var(--blue-60)' : 'var(--text-placeholder)'
      }
    }, v), /*#__PURE__*/React.createElement("span", {
      style: {
        width: '100%',
        maxWidth: 38,
        height: h,
        background: last ? 'var(--blue-60)' : 'var(--gray-20)'
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        color: last ? 'var(--text-secondary)' : 'var(--text-placeholder)'
      }
    }, weeks[i]));
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--gray-100)',
      color: '#fff',
      padding: '24px 28px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      gap: 18
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      color: 'var(--green-50)'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "trending-up",
    size: 26,
    color: "var(--green-50)"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 40,
      fontWeight: 300,
      fontFamily: 'var(--font-mono)'
    }
  }, "+", d.deltaPct, "%")), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      color: 'var(--gray-30)',
      marginTop: 4
    }
  }, "vs. last week (", d.totalLastWeek, " \u2192 ", d.totalThisWeek, ")")), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 1,
      background: 'var(--gray-80)'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 28
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 26,
      fontWeight: 300
    }
  }, d.totalThisWeek), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--gray-40)'
    }
  }, "this week")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 26,
      fontWeight: 300,
      color: 'var(--blue-40)'
    }
  }, d.newQuestionTypes), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: 'var(--gray-40)'
    }
  }, "new types"))))), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 15,
      fontWeight: 600,
      marginBottom: 12,
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "activity",
    size: 16,
    color: "var(--blue-60)"
  }), " Questions this week, by frequency"), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: '2px solid var(--gray-100)'
    }
  }, d.groups.map(g => /*#__PURE__*/React.createElement("div", {
    key: g.rank,
    style: {
      display: 'grid',
      gridTemplateColumns: '24px 64px 1fr 160px 40px',
      alignItems: 'center',
      gap: 16,
      padding: '12px 0',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 14,
      color: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-50)'
    }
  }, String(g.rank).padStart(2, '0')), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement(MovementBadge, {
    movement: g.movement
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, g.question), /*#__PURE__*/React.createElement("span", {
    style: {
      height: 8,
      background: 'var(--gray-10)',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      inset: '0 auto 0 0',
      width: `${Math.max(8, g.count / max * 100)}%`,
      background: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-40)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 14,
      fontWeight: 500,
      textAlign: 'right'
    }
  }, g.count, "\xD7"))))));
}
window.WirPulse = WirPulse;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/explore/WirPulse.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/explore/WirScorecard.jsx
try { (() => {
// OPTION B — "Scorecard": analytics-dense KPI tiles + ranked list + movers rail.
function WirScorecard() {
  const {
    MetricTile,
    Tag,
    Button
  } = DS_NS();
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;
  const movers = d.groups.filter(g => g.movement === 'new' || typeof g.movement === 'number' && g.movement > 0).slice(0, 4);
  const kpi = {
    background: 'var(--layer-02)',
    borderLeft: '3px solid var(--blue-60)',
    padding: '16px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: 8
  };
  const kpiLabel = {
    fontSize: 11,
    textTransform: 'uppercase',
    letterSpacing: '.32px',
    color: 'var(--text-helper)',
    fontWeight: 500
  };
  const kpiNum = {
    fontSize: 32,
    fontWeight: 300,
    lineHeight: 1,
    letterSpacing: '-.02em'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'var(--gray-10)'
    }
  }, /*#__PURE__*/React.createElement(AppShellHeader, {
    active: "week"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      overflow: 'hidden',
      padding: '28px 40px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'space-between',
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 24,
      fontWeight: 300,
      letterSpacing: '-.01em'
    }
  }, "Week in Review"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontFamily: 'var(--font-mono)',
      color: 'var(--text-helper)',
      marginTop: 2
    }
  }, d.weekLabel, " \xB7 vs. May 26 \u2013 Jun 1")), /*#__PURE__*/React.createElement(Button, {
    variant: "tertiary",
    size: "md",
    icon: /*#__PURE__*/React.createElement(Icon, {
      name: "send",
      size: 16
    })
  }, "Post to Slack")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 1,
      background: 'var(--border-subtle)',
      border: '1px solid var(--border-subtle)',
      marginBottom: 24
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: kpi
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiLabel
  }, "Questions this week"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiNum
  }, d.totalThisWeek), /*#__PURE__*/React.createElement(DeltaBadge, {
    value: d.deltaPct
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      ...kpi,
      borderLeftColor: 'var(--purple-60)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiLabel
  }, "New question types"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiNum
  }, d.newQuestionTypes), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: 'var(--text-secondary)'
    }
  }, "of ", d.groupsThisWeek))), /*#__PURE__*/React.createElement("div", {
    style: {
      ...kpi,
      borderLeftColor: 'var(--teal-60)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiLabel
  }, "Active groups"), /*#__PURE__*/React.createElement("span", {
    style: kpiNum
  }, d.groupsThisWeek)), /*#__PURE__*/React.createElement("div", {
    style: {
      ...kpi,
      borderLeftColor: 'var(--gray-60)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiLabel
  }, "Answered"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: kpiNum
  }, d.answered), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: 'var(--text-secondary)'
    }
  }, "resolved")))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 300px',
      gap: 24,
      alignItems: 'start'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      background: '#fff',
      border: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '14px 18px',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      fontWeight: 600,
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "list-ordered",
    size: 16,
    color: "var(--blue-60)"
  }), " Ranked this week"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: 'var(--text-helper)'
    }
  }, "\u0394 = rank vs last week")), d.groups.map(g => /*#__PURE__*/React.createElement("div", {
    key: g.rank,
    style: {
      display: 'grid',
      gridTemplateColumns: '26px 1fr 90px 40px 44px',
      alignItems: 'center',
      gap: 12,
      padding: '12px 18px',
      borderBottom: '1px solid var(--border-subtle)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 14,
      color: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-50)',
      textAlign: 'right'
    }
  }, String(g.rank).padStart(2, '0')), /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13.5,
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, g.question), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      fontFamily: 'var(--font-mono)',
      color: 'var(--text-placeholder)',
      marginTop: 2
    }
  }, g.keywords.slice(0, 3).join(' · '))), /*#__PURE__*/React.createElement("span", {
    style: {
      height: 5,
      background: 'var(--gray-10)',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      inset: '0 auto 0 0',
      width: `${Math.max(8, g.count / max * 100)}%`,
      background: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-40)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      textAlign: 'center'
    }
  }, /*#__PURE__*/React.createElement(MovementBadge, {
    movement: g.movement
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 13,
      fontWeight: 500,
      textAlign: 'right'
    }
  }, g.count, "\xD7")))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      background: '#fff',
      border: '1px solid var(--border-subtle)',
      padding: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 600,
      marginBottom: 12,
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "trending-up",
    size: 15,
    color: "var(--green-60)"
  }), " Biggest movers"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 10
    }
  }, movers.map(g => /*#__PURE__*/React.createElement("div", {
    key: g.rank,
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement(MovementBadge, {
    movement: g.movement
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12.5,
      color: 'var(--text-secondary)',
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, g.topic))))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: '#fff',
      border: '1px solid var(--border-subtle)',
      padding: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 600,
      marginBottom: 12
    }
  }, "New topics this week"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 6
    }
  }, d.groups.filter(g => g.movement === 'new').map(g => /*#__PURE__*/React.createElement(Tag, {
    key: g.rank,
    color: "blue",
    size: "sm"
  }, g.topic))))))));
}
window.WirScorecard = WirScorecard;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/explore/WirScorecard.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/explore/design-canvas.jsx
try { (() => {
// @ds-adherence-ignore -- omelette starter scaffold (raw elements/hex/px by design)

/* BEGIN USAGE */
// DesignCanvas.jsx — Figma-ish design canvas wrapper
// Warm gray grid bg + Sections + Artboards + PostIt notes.
// Exports (to window): DesignCanvas, DCSection, DCArtboard, DCPostIt.
// Artboards are reorderable (grip-drag), deletable, labels/titles are
// inline-editable, and any artboard can be opened in a fullscreen focus
// overlay (←/→/Esc). State persists to a .design-canvas.state.json sidecar
// via the host bridge. No assets, no deps.
//
// Usage:
//   <DesignCanvas>
//     <DCSection id="onboarding" title="Onboarding" subtitle="First-run variants">
//       <DCArtboard id="a" label="A · Dusk" width={260} height={480}>…</DCArtboard>
//       <DCArtboard id="b" label="B · Minimal" width={260} height={480}>…</DCArtboard>
//     </DCSection>
//   </DesignCanvas>
//
// Artboards are static design frames, not scroll regions — never use
// height: 100% + overflow: auto/scroll on inner elements; size each artboard
// to fit its content (explicit pixel height, or let it grow).
/* END USAGE */

const DC = {
  bg: '#f0eee9',
  grid: 'rgba(0,0,0,0.06)',
  label: 'rgba(60,50,40,0.7)',
  title: 'rgba(40,30,20,0.85)',
  subtitle: 'rgba(60,50,40,0.6)',
  postitBg: '#fef4a8',
  postitText: '#5a4a2a',
  font: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'
};

// One-time CSS injection (classes are dc-prefixed so they don't collide with
// the hosted design's own styles).
if (typeof document !== 'undefined' && !document.getElementById('dc-styles')) {
  const s = document.createElement('style');
  s.id = 'dc-styles';
  s.textContent = ['.dc-editable{cursor:text;outline:none;white-space:nowrap;border-radius:3px;padding:0 2px;margin:0 -2px}', '.dc-editable:focus{background:#fff;box-shadow:0 0 0 1.5px #c96442}', '[data-dc-slot]{transition:transform .18s cubic-bezier(.2,.7,.3,1)}', '[data-dc-slot].dc-dragging{transition:none;z-index:10;pointer-events:none}', '[data-dc-slot].dc-dragging .dc-card{box-shadow:0 12px 40px rgba(0,0,0,.25),0 0 0 2px #c96442;transform:scale(1.02)}',
  // isolation:isolate contains artboard content's z-indexes so a
  // z-indexed child (sticky navbar etc.) can't paint over .dc-header or
  // the .dc-menu popover that drops into the top of the card.
  '.dc-card{isolation:isolate;transition:box-shadow .15s,transform .15s}', '.dc-card *{scrollbar-width:none}', '.dc-card *::-webkit-scrollbar{display:none}',
  // Per-artboard header: grip + label on the left, delete/expand on the
  // right. Single flex row; when the artboard's on-screen width is too
  // narrow for both the label yields (ellipsis, then hidden entirely below
  // ~4ch via the container query) and the buttons stay on the row.
  '.dc-header{position:absolute;bottom:100%;left:-4px;margin-bottom:calc(4px * var(--dc-inv-zoom,1));z-index:2;', '  display:flex;align-items:center;container-type:inline-size}', '.dc-labelrow{display:flex;align-items:center;gap:4px;height:24px;flex:1 1 auto;min-width:0}', '.dc-grip{flex:0 0 auto;cursor:grab;display:flex;align-items:center;padding:5px 4px;border-radius:4px;transition:background .12s,opacity .12s}', '.dc-grip:hover{background:rgba(0,0,0,.08)}', '.dc-grip:active{cursor:grabbing}', '.dc-labeltext{flex:1 1 auto;min-width:0;cursor:pointer;border-radius:4px;padding:3px 6px;', '  display:flex;align-items:center;transition:background .12s;overflow:hidden}',
  // Below ~4ch of label room: hide the label entirely, and drop the grip to
  // hover-only (same reveal rule as .dc-btns) so a narrow header is clean
  // until the card is moused.
  '@container (max-width: 110px){', '  .dc-labeltext{display:none}', '  .dc-grip{opacity:0}', '  [data-dc-slot]:hover .dc-grip{opacity:1}', '}', '.dc-labeltext:hover{background:rgba(0,0,0,.05)}', '.dc-labeltext .dc-editable{overflow:hidden;text-overflow:ellipsis;max-width:100%}', '.dc-labeltext .dc-editable:focus{overflow:visible;text-overflow:clip}', '.dc-btns{flex:0 0 auto;margin-left:auto;display:flex;gap:2px;opacity:0;transition:opacity .12s}', '[data-dc-slot]:hover .dc-btns,.dc-btns:has(.dc-menu){opacity:1}', '.dc-expand,.dc-kebab{width:22px;height:22px;border-radius:5px;border:none;cursor:pointer;padding:0;', '  background:transparent;color:rgba(60,50,40,.7);display:flex;align-items:center;justify-content:center;', '  font:inherit;transition:background .12s,color .12s}', '.dc-expand:hover,.dc-kebab:hover{background:rgba(0,0,0,.06);color:#2a251f}',
  // Slot hosting an open menu floats above later siblings (which otherwise
  // paint on top — same z-index:auto, later DOM order) so the popup isn't
  // clipped by the next card.
  '[data-dc-slot]:has(.dc-menu){z-index:10}', '.dc-menu{position:absolute;top:100%;right:0;margin-top:4px;background:#fff;border-radius:8px;', '  box-shadow:0 8px 28px rgba(0,0,0,.18),0 0 0 1px rgba(0,0,0,.05);padding:4px;min-width:160px;z-index:10}', '.dc-menu button{display:block;width:100%;padding:7px 10px;border:0;background:transparent;', '  border-radius:5px;font-family:inherit;font-size:13px;font-weight:500;line-height:1.2;', '  color:#29261b;cursor:pointer;text-align:left;transition:background .12s;white-space:nowrap}', '.dc-menu button:hover{background:rgba(0,0,0,.05)}', '.dc-menu hr{border:0;border-top:1px solid rgba(0,0,0,.08);margin:4px 2px}', '.dc-menu .dc-danger{color:#c96442}', '.dc-menu .dc-danger:hover{background:rgba(201,100,66,.1)}',
  // Chrome (titles / labels / buttons) counter-scales against the viewport
  // zoom so it stays a constant on-screen size. --dc-inv-zoom is set by
  // DCViewport on every transform update and inherits to all descendants —
  // any overlay inside the world (e.g. a TweaksPanel on an artboard) can use
  // it the same way.
  //
  // The header uses transform:scale (out-of-flow, so layout impact doesn't
  // matter) with its world-space width set to card-width / inv-zoom so that
  // after counter-scaling its on-screen width exactly matches the card's —
  // that's what lets the container query + text-overflow behave against the
  // card's visible edge at every zoom level.
  //
  // The section head uses CSS zoom instead of transform so its layout box
  // grows with the counter-scale, pushing the card row down — otherwise the
  // constant-screen-size title would overflow into the (shrinking) world-
  // space gap and overlap the artboard headers at low zoom.
  '.dc-header{width:calc((100% + 4px) / var(--dc-inv-zoom,1));', '  transform:scale(var(--dc-inv-zoom,1));transform-origin:bottom left}', '.dc-sectionhead{zoom:var(--dc-inv-zoom,1)}'].join('\n');
  document.head.appendChild(s);
}
const DCCtx = React.createContext(null);

// Recursively unwrap React.Fragment so <>…</> grouping doesn't hide
// DCSection/DCArtboard children from the type-based walks below.
function dcFlatten(children) {
  const out = [];
  React.Children.forEach(children, c => {
    if (c && c.type === React.Fragment) out.push(...dcFlatten(c.props.children));else out.push(c);
  });
  return out;
}

// ─────────────────────────────────────────────────────────────
// DesignCanvas — stateful wrapper around the pan/zoom viewport.
// Owns runtime state (per-section order, renamed titles/labels, hidden
// artboards, focused artboard). Order/titles/labels/hidden persist to a
// .design-canvas.state.json
// sidecar next to the HTML. Reads go via plain fetch() so the saved
// arrangement is visible anywhere the HTML + sidecar are served together
// (omelette preview, direct link, downloaded zip). Writes go through the
// host's window.omelette bridge — editing requires the omelette runtime.
// Focus is ephemeral.
// ─────────────────────────────────────────────────────────────
const DC_STATE_FILE = '.design-canvas.state.json';
function DesignCanvas({
  children,
  minScale,
  maxScale,
  style
}) {
  const [state, setState] = React.useState({
    sections: {},
    focus: null
  });
  // Hold rendering until the sidecar read settles so the saved order/titles
  // appear on first paint (no source-order flash). didRead gates writes until
  // the read settles so the empty initial state can't clobber a slow read;
  // skipNextWrite suppresses the one echo-write that would otherwise follow
  // hydration.
  const [ready, setReady] = React.useState(false);
  const didRead = React.useRef(false);
  const skipNextWrite = React.useRef(false);
  React.useEffect(() => {
    let off = false;
    fetch('./' + DC_STATE_FILE).then(r => r.ok ? r.json() : null).then(saved => {
      if (off || !saved || !saved.sections) return;
      skipNextWrite.current = true;
      setState(s => ({
        ...s,
        sections: saved.sections
      }));
    }).catch(() => {}).finally(() => {
      didRead.current = true;
      if (!off) setReady(true);
    });
    const t = setTimeout(() => {
      if (!off) setReady(true);
    }, 150);
    return () => {
      off = true;
      clearTimeout(t);
    };
  }, []);
  React.useEffect(() => {
    if (!didRead.current) return;
    if (skipNextWrite.current) {
      skipNextWrite.current = false;
      return;
    }
    const t = setTimeout(() => {
      window.omelette?.writeFile(DC_STATE_FILE, JSON.stringify({
        sections: state.sections
      })).catch(() => {});
    }, 250);
    return () => clearTimeout(t);
  }, [state.sections]);

  // Build registries synchronously from children so FocusOverlay can read
  // them in the same render. Fragments are flattened; wrapping in other
  // elements still opts out of focus/reorder.
  const registry = {}; // slotId -> { sectionId, artboard }
  const sectionMeta = {}; // sectionId -> { title, subtitle, slotIds[] }
  const sectionOrder = [];
  dcFlatten(children).forEach(sec => {
    if (!sec || sec.type !== DCSection) return;
    const sid = sec.props.id ?? sec.props.title;
    if (!sid) return;
    sectionOrder.push(sid);
    const persisted = state.sections[sid] || {};
    const abs = [];
    dcFlatten(sec.props.children).forEach(ab => {
      if (!ab || ab.type !== DCArtboard) return;
      const aid = ab.props.id ?? ab.props.label;
      if (aid) abs.push([aid, ab]);
    });
    // hidden is scoped to one source revision — when the agent regenerates
    // (artboard-ID set changes), prior deletes don't apply to new content.
    const srcKey = abs.map(([k]) => k).join('\x1f');
    const hidden = persisted.srcKey === srcKey ? persisted.hidden || [] : [];
    const srcIds = [];
    abs.forEach(([aid, ab]) => {
      if (hidden.includes(aid)) return;
      registry[`${sid}/${aid}`] = {
        sectionId: sid,
        artboard: ab
      };
      srcIds.push(aid);
    });
    const kept = (persisted.order || []).filter(k => srcIds.includes(k));
    sectionMeta[sid] = {
      title: persisted.title ?? sec.props.title,
      subtitle: sec.props.subtitle,
      slotIds: [...kept, ...srcIds.filter(k => !kept.includes(k))]
    };
  });
  const api = React.useMemo(() => ({
    state,
    section: id => state.sections[id] || {},
    patchSection: (id, p) => setState(s => ({
      ...s,
      sections: {
        ...s.sections,
        [id]: {
          ...s.sections[id],
          ...(typeof p === 'function' ? p(s.sections[id] || {}) : p)
        }
      }
    })),
    setFocus: slotId => setState(s => ({
      ...s,
      focus: slotId
    }))
  }), [state]);

  // Esc exits focus; any outside pointerdown commits an in-progress rename.
  React.useEffect(() => {
    const onKey = e => {
      if (e.key === 'Escape') api.setFocus(null);
    };
    const onPd = e => {
      const ae = document.activeElement;
      if (ae && ae.isContentEditable && !ae.contains(e.target)) ae.blur();
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('pointerdown', onPd, true);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('pointerdown', onPd, true);
    };
  }, [api]);
  return /*#__PURE__*/React.createElement(DCCtx.Provider, {
    value: api
  }, /*#__PURE__*/React.createElement(DCViewport, {
    minScale: minScale,
    maxScale: maxScale,
    style: style
  }, ready && children), state.focus && registry[state.focus] && /*#__PURE__*/React.createElement(DCFocusOverlay, {
    entry: registry[state.focus],
    sectionMeta: sectionMeta,
    sectionOrder: sectionOrder
  }));
}

// ─────────────────────────────────────────────────────────────
// DCViewport — transform-based pan/zoom (internal)
//
// Input mapping (Figma-style):
//   • trackpad pinch  → zoom   (ctrlKey wheel; Safari gesture* events)
//   • trackpad scroll → pan    (two-finger)
//   • mouse wheel     → zoom   (notched; distinguished from trackpad scroll)
//   • middle-drag / primary-drag-on-bg → pan
//
// Transform state lives in a ref and is written straight to the DOM
// (translate3d + will-change) so wheel ticks don't go through React —
// keeps pans at 60fps on dense canvases.
// ─────────────────────────────────────────────────────────────
function DCViewport({
  children,
  minScale = 0.1,
  maxScale = 8,
  style = {}
}) {
  const vpRef = React.useRef(null);
  const worldRef = React.useRef(null);
  const tf = React.useRef({
    x: 0,
    y: 0,
    scale: 1
  });
  // Persist viewport across reloads so the user lands back where they were
  // after an agent edit or browser refresh. The sandbox origin is already
  // per-project; pathname keeps multiple canvas files in one project apart.
  const tfKey = 'dc-viewport:' + location.pathname;
  const saveT = React.useRef(0);
  const lastPostedScale = React.useRef();
  const apply = React.useCallback(() => {
    const {
      x,
      y,
      scale
    } = tf.current;
    const el = worldRef.current;
    if (!el) return;
    el.style.transform = `translate3d(${x}px, ${y}px, 0) scale(${scale})`;
    // Exposed for zoom-invariant chrome (labels, buttons, TweaksPanel).
    el.style.setProperty('--dc-inv-zoom', String(1 / scale));
    // Keep the host toolbar's % readout in sync with the canvas scale. Pan
    // ticks leave scale unchanged — skip the cross-frame post for those.
    if (lastPostedScale.current !== scale) {
      lastPostedScale.current = scale;
      window.parent.postMessage({
        type: '__dc_zoom',
        scale
      }, '*');
    }
    clearTimeout(saveT.current);
    saveT.current = setTimeout(() => {
      try {
        localStorage.setItem(tfKey, JSON.stringify(tf.current));
      } catch {}
    }, 200);
  }, [tfKey]);
  React.useLayoutEffect(() => {
    const flush = () => {
      clearTimeout(saveT.current);
      try {
        localStorage.setItem(tfKey, JSON.stringify(tf.current));
      } catch {}
    };
    try {
      const s = JSON.parse(localStorage.getItem(tfKey) || 'null');
      if (s && Number.isFinite(s.x) && Number.isFinite(s.y) && Number.isFinite(s.scale)) {
        tf.current = {
          x: s.x,
          y: s.y,
          scale: Math.min(maxScale, Math.max(minScale, s.scale))
        };
        apply();
      }
    } catch {}
    // Flush on pagehide and unmount so a reload within the 200ms debounce
    // window doesn't drop the last pan/zoom.
    window.addEventListener('pagehide', flush);
    return () => {
      window.removeEventListener('pagehide', flush);
      flush();
    };
  }, []);
  React.useEffect(() => {
    const vp = vpRef.current;
    if (!vp) return;
    const zoomAt = (cx, cy, factor) => {
      const r = vp.getBoundingClientRect();
      const px = cx - r.left,
        py = cy - r.top;
      const t = tf.current;
      const next = Math.min(maxScale, Math.max(minScale, t.scale * factor));
      const k = next / t.scale;
      // --dc-inv-zoom consumers (.dc-sectionhead's CSS zoom, each section's
      // marginBottom) reflow on every scale change, vertically shifting the
      // world layout — so a world point mathematically pinned under the cursor
      // drifts as you zoom (content creeps up on zoom-in, down on zoom-out).
      // Anchor the DOM element under the cursor instead: record its screen Y,
      // apply the transform + --dc-inv-zoom, then cancel whatever vertical
      // drift the reflow introduced so it stays put on screen.
      let marker = null,
        markerY0 = 0;
      if (k !== 1) {
        const hit = document.elementFromPoint(cx, cy);
        marker = hit && hit.closest ? hit.closest('[data-dc-slot],[data-dc-section]') : null;
        if (marker) markerY0 = marker.getBoundingClientRect().top;
      }
      // keep the world point under the cursor fixed
      t.x = px - (px - t.x) * k;
      t.y = py - (py - t.y) * k;
      t.scale = next;
      apply();
      if (marker) {
        // A pure zoom around (cx, cy) maps screen Y → cy + (Y - cy) * k. Any
        // departure after the --dc-inv-zoom reflow is the layout drift.
        const drift = marker.getBoundingClientRect().top - (cy + (markerY0 - cy) * k);
        if (Math.abs(drift) > 0.1) {
          t.y -= drift;
          apply();
        }
      }
    };

    // Mouse-wheel vs trackpad-scroll heuristic. A physical wheel sends
    // line-mode deltas (Firefox) or large integer pixel deltas with no X
    // component (Chrome/Safari, typically multiples of 100/120). Trackpad
    // two-finger scroll sends small/fractional pixel deltas, often with
    // non-zero deltaX. ctrlKey is set by the browser for trackpad pinch.
    const isMouseWheel = e => e.deltaMode !== 0 || e.deltaX === 0 && Number.isInteger(e.deltaY) && Math.abs(e.deltaY) >= 40;
    const onWheel = e => {
      e.preventDefault();
      if (isGesturing) return; // Safari: gesture* owns the pinch — discard concurrent wheels
      if ((e.ctrlKey || e.metaKey) && !isMouseWheel(e)) {
        // trackpad pinch, or ctrl/cmd + smooth-scroll mouse. Notched
        // wheels fall through to the fixed-step branch below.
        zoomAt(e.clientX, e.clientY, Math.exp(-e.deltaY * 0.01));
      } else if (isMouseWheel(e)) {
        // notched mouse wheel — fixed-ratio step per click
        zoomAt(e.clientX, e.clientY, Math.exp(-Math.sign(e.deltaY) * 0.18));
      } else {
        // trackpad two-finger scroll — pan
        tf.current.x -= e.deltaX;
        tf.current.y -= e.deltaY;
        apply();
      }
    };

    // Safari sends native gesture* events for trackpad pinch with a smooth
    // e.scale; preferring these over the ctrl+wheel fallback gives a much
    // better feel there. No-ops on other browsers. Safari also fires
    // ctrlKey wheel events during the same pinch — isGesturing makes
    // onWheel drop those entirely so they neither zoom nor pan.
    let gsBase = 1;
    let isGesturing = false;
    const onGestureStart = e => {
      e.preventDefault();
      isGesturing = true;
      gsBase = tf.current.scale;
    };
    const onGestureChange = e => {
      e.preventDefault();
      zoomAt(e.clientX, e.clientY, gsBase * e.scale / tf.current.scale);
    };
    const onGestureEnd = e => {
      e.preventDefault();
      isGesturing = false;
    };

    // Drag-pan: middle button anywhere, or primary button on canvas
    // background (anything that isn't an artboard or an inline editor).
    let drag = null;
    const onPointerDown = e => {
      const onBg = !e.target.closest('[data-dc-slot], .dc-editable');
      if (!(e.button === 1 || e.button === 0 && onBg)) return;
      e.preventDefault();
      vp.setPointerCapture(e.pointerId);
      drag = {
        id: e.pointerId,
        lx: e.clientX,
        ly: e.clientY
      };
      vp.style.cursor = 'grabbing';
    };
    const onPointerMove = e => {
      if (!drag || e.pointerId !== drag.id) return;
      tf.current.x += e.clientX - drag.lx;
      tf.current.y += e.clientY - drag.ly;
      drag.lx = e.clientX;
      drag.ly = e.clientY;
      apply();
    };
    const onPointerUp = e => {
      if (!drag || e.pointerId !== drag.id) return;
      vp.releasePointerCapture(e.pointerId);
      drag = null;
      vp.style.cursor = '';
    };

    // Host-driven zoom (toolbar % menu). Zooms around viewport centre so the
    // visible midpoint stays fixed — matching the host's iframe-zoom feel.
    const onHostMsg = e => {
      const d = e.data;
      if (d && d.type === '__dc_set_zoom' && typeof d.scale === 'number') {
        const r = vp.getBoundingClientRect();
        zoomAt(r.left + r.width / 2, r.top + r.height / 2, d.scale / tf.current.scale);
      } else if (d && d.type === '__dc_probe') {
        // Host's [readyGen] reset asks whether a canvas is present; it
        // fires on the iframe's native 'load', which for canvases with
        // images/fonts is after our mount-time announce, so re-announce.
        // Clear the pan-tick guard so apply() re-posts the current scale
        // even if it's unchanged — the host just reset dcScale to 1.
        window.parent.postMessage({
          type: '__dc_present'
        }, '*');
        lastPostedScale.current = undefined;
        apply();
      }
    };
    window.addEventListener('message', onHostMsg);
    // Announce canvas mode so the host toolbar proxies its % control here
    // instead of scaling the iframe element (which would just shrink the
    // viewport window of an infinite canvas). The apply() that follows emits
    // the initial __dc_zoom so the toolbar % is correct before first pinch.
    // lastPostedScale reset mirrors the __dc_probe handler: the layout
    // effect's restore-path apply() may already have posted the restored
    // scale (before __dc_present), so clear the guard to re-post it in order.
    window.parent.postMessage({
      type: '__dc_present'
    }, '*');
    lastPostedScale.current = undefined;
    apply();
    vp.addEventListener('wheel', onWheel, {
      passive: false
    });
    vp.addEventListener('gesturestart', onGestureStart, {
      passive: false
    });
    vp.addEventListener('gesturechange', onGestureChange, {
      passive: false
    });
    vp.addEventListener('gestureend', onGestureEnd, {
      passive: false
    });
    vp.addEventListener('pointerdown', onPointerDown);
    vp.addEventListener('pointermove', onPointerMove);
    vp.addEventListener('pointerup', onPointerUp);
    vp.addEventListener('pointercancel', onPointerUp);
    return () => {
      window.removeEventListener('message', onHostMsg);
      vp.removeEventListener('wheel', onWheel);
      vp.removeEventListener('gesturestart', onGestureStart);
      vp.removeEventListener('gesturechange', onGestureChange);
      vp.removeEventListener('gestureend', onGestureEnd);
      vp.removeEventListener('pointerdown', onPointerDown);
      vp.removeEventListener('pointermove', onPointerMove);
      vp.removeEventListener('pointerup', onPointerUp);
      vp.removeEventListener('pointercancel', onPointerUp);
    };
  }, [apply, minScale, maxScale]);
  const gridSvg = `url("data:image/svg+xml,%3Csvg width='120' height='120' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M120 0H0v120' fill='none' stroke='${encodeURIComponent(DC.grid)}' stroke-width='1'/%3E%3C/svg%3E")`;
  return /*#__PURE__*/React.createElement("div", {
    ref: vpRef,
    className: "design-canvas",
    style: {
      height: '100vh',
      width: '100vw',
      background: DC.bg,
      overflow: 'hidden',
      overscrollBehavior: 'none',
      touchAction: 'none',
      position: 'relative',
      fontFamily: DC.font,
      boxSizing: 'border-box',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    ref: worldRef,
    style: {
      position: 'absolute',
      top: 0,
      left: 0,
      transformOrigin: '0 0',
      willChange: 'transform',
      width: 'max-content',
      minWidth: '100%',
      minHeight: '100%',
      padding: '60px 0 80px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: -6000,
      backgroundImage: gridSvg,
      backgroundSize: '120px 120px',
      pointerEvents: 'none',
      zIndex: -1
    }
  }), children));
}

// ─────────────────────────────────────────────────────────────
// DCSection — editable title + h-row of artboards in persisted order
// ─────────────────────────────────────────────────────────────
function DCSection({
  id,
  title,
  subtitle,
  children,
  gap = 48
}) {
  const ctx = React.useContext(DCCtx);
  const sid = id ?? title;
  const all = React.Children.toArray(dcFlatten(children));
  const artboards = all.filter(c => c && c.type === DCArtboard);
  const rest = all.filter(c => !(c && c.type === DCArtboard));
  const sec = ctx && sid && ctx.section(sid) || {};
  // Must match DesignCanvas's srcKey computation exactly (it filters falsy
  // IDs), or onDelete persists a srcKey that DesignCanvas never recognizes.
  const allIds = artboards.map(a => a.props.id ?? a.props.label).filter(Boolean);
  const srcKey = allIds.join('\x1f');
  const hidden = sec.srcKey === srcKey ? sec.hidden || [] : [];
  const srcOrder = allIds.filter(k => !hidden.includes(k));
  const order = React.useMemo(() => {
    const kept = (sec.order || []).filter(k => srcOrder.includes(k));
    return [...kept, ...srcOrder.filter(k => !kept.includes(k))];
  }, [sec.order, srcOrder.join('|')]);
  const byId = Object.fromEntries(artboards.map(a => [a.props.id ?? a.props.label, a]));

  // marginBottom counter-scales so the on-screen gap between sections stays
  // constant — otherwise at low zoom the (world-space) gap collapses while
  // the screen-constant sectionhead below it doesn't, and the title reads as
  // belonging to the section above. paddingBottom below is just enough for
  // the 24px artboard-header (abs-positioned above each card) plus ~8px, so
  // the title sits tight against its own row at every zoom.
  return /*#__PURE__*/React.createElement("div", {
    "data-dc-section": sid,
    style: {
      marginBottom: 'calc(80px * var(--dc-inv-zoom, 1))',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 60px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "dc-sectionhead",
    style: {
      paddingBottom: 36
    }
  }, /*#__PURE__*/React.createElement(DCEditable, {
    tag: "div",
    value: sec.title ?? title,
    onChange: v => ctx && sid && ctx.patchSection(sid, {
      title: v
    }),
    style: {
      fontSize: 28,
      fontWeight: 600,
      color: DC.title,
      letterSpacing: -0.4,
      marginBottom: 6,
      display: 'inline-block'
    }
  }), subtitle && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 16,
      color: DC.subtitle
    }
  }, subtitle))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap,
      padding: '0 60px',
      alignItems: 'flex-start',
      width: 'max-content'
    }
  }, order.map(k => /*#__PURE__*/React.createElement(DCArtboardFrame, {
    key: k,
    sectionId: sid,
    artboard: byId[k],
    order: order,
    label: (sec.labels || {})[k] ?? byId[k].props.label,
    onRename: v => ctx && ctx.patchSection(sid, x => ({
      labels: {
        ...x.labels,
        [k]: v
      }
    })),
    onReorder: next => ctx && ctx.patchSection(sid, {
      order: next
    }),
    onDelete: () => ctx && ctx.patchSection(sid, x => ({
      hidden: [...(x.srcKey === srcKey ? x.hidden || [] : []), k],
      srcKey
    })),
    onFocus: () => ctx && ctx.setFocus(`${sid}/${k}`)
  }))), rest);
}

// DCArtboard — marker; rendered by DCArtboardFrame via DCSection.
function DCArtboard() {
  return null;
}

// Per-artboard export (kind: 'png' | 'html'). Both paths share the same
// self-contained clone: computed styles baked in, @font-face / <img> /
// inline-style background-image urls inlined as data URIs. PNG wraps the
// clone in foreignObject→canvas at 3× the artboard's natural width×height
// (same pipeline the host uses for page captures); HTML wraps it in a
// minimal standalone document. Both are independent of viewport zoom.
async function dcExport(node, w, h, name, kind) {
  try {
    await document.fonts.ready;
  } catch {}
  const toDataURL = url => fetch(url).then(r => r.blob()).then(b => new Promise(res => {
    const fr = new FileReader();
    fr.onload = () => res(fr.result);
    fr.onerror = () => res(url);
    fr.readAsDataURL(b);
  })).catch(() => url);

  // Collect @font-face rules. ss.cssRules throws SecurityError on
  // cross-origin sheets (e.g. fonts.googleapis.com) — in that case fetch
  // the CSS text directly (those endpoints send ACAO:*) and regex-extract
  // the blocks. @import and @media/@supports are walked so nested
  // @font-face rules aren't missed.
  const fontRules = [],
    pending = [],
    seen = new Set();
  const scrapeCss = href => {
    if (seen.has(href)) return;
    seen.add(href);
    pending.push(fetch(href).then(r => r.text()).then(css => {
      for (const m of css.match(/@font-face\s*{[^}]*}/g) || []) fontRules.push({
        css: m,
        base: href
      });
      for (const m of css.matchAll(/@import\s+(?:url\()?['"]?([^'")\s;]+)/g)) scrapeCss(new URL(m[1], href).href);
    }).catch(() => {}));
  };
  const walk = (rules, base) => {
    for (const r of rules) {
      if (r.type === CSSRule.FONT_FACE_RULE) fontRules.push({
        css: r.cssText,
        base
      });else if (r.type === CSSRule.IMPORT_RULE && r.styleSheet) {
        const ibase = r.styleSheet.href || base;
        try {
          walk(r.styleSheet.cssRules, ibase);
        } catch {
          scrapeCss(ibase);
        }
      } else if (r.cssRules) walk(r.cssRules, base);
    }
  };
  for (const ss of document.styleSheets) {
    const base = ss.href || location.href;
    try {
      walk(ss.cssRules, base);
    } catch {
      if (ss.href) scrapeCss(ss.href);
    }
  }
  while (pending.length) await pending.shift();
  const fontCss = (await Promise.all(fontRules.map(async rule => {
    let out = rule.css,
      m;
    const re = /url\((['"]?)([^'")]+)\1\)/g;
    while (m = re.exec(rule.css)) {
      if (m[2].indexOf('data:') === 0) continue;
      let abs;
      try {
        abs = new URL(m[2], rule.base).href;
      } catch {
        continue;
      }
      out = out.split(m[0]).join('url("' + (await toDataURL(abs)) + '")');
    }
    return out;
  }))).join('\n');
  const cloneStyled = src => {
    if (src.nodeType === 8 || src.nodeType === 1 && src.tagName === 'SCRIPT') return document.createTextNode('');
    const dst = src.cloneNode(false);
    if (src.nodeType === 1) {
      const cs = getComputedStyle(src);
      let txt = '';
      for (let i = 0; i < cs.length; i++) txt += cs[i] + ':' + cs.getPropertyValue(cs[i]) + ';';
      dst.setAttribute('style', txt + 'animation:none;transition:none;');
      if (src.tagName === 'CANVAS') try {
        const im = document.createElement('img');
        im.src = src.toDataURL();
        im.setAttribute('style', txt);
        return im;
      } catch {}
    }
    for (let c = src.firstChild; c; c = c.nextSibling) dst.appendChild(cloneStyled(c));
    return dst;
  };
  const clone = cloneStyled(node);
  clone.setAttribute('xmlns', 'http://www.w3.org/1999/xhtml');
  // Drop the card's own shadow/radius so the export is a flush w×h rect;
  // the artboard's own background (if any) is already in the computed style.
  clone.style.boxShadow = 'none';
  clone.style.borderRadius = '0';
  const jobs = [];
  clone.querySelectorAll('img').forEach(el => {
    const s = el.getAttribute('src');
    if (s && s.indexOf('data:') !== 0) jobs.push(toDataURL(el.src).then(d => el.setAttribute('src', d)));
  });
  [clone, ...clone.querySelectorAll('*')].forEach(el => {
    const bg = el.style.backgroundImage;
    if (!bg) return;
    let m;
    const re = /url\(["']?([^"')]+)["']?\)/g;
    while (m = re.exec(bg)) {
      const tok = m[0],
        url = m[1];
      if (url.indexOf('data:') === 0) continue;
      jobs.push(toDataURL(url).then(d => {
        el.style.backgroundImage = el.style.backgroundImage.split(tok).join('url("' + d + '")');
      }));
    }
  });
  await Promise.all(jobs);
  const xml = new XMLSerializer().serializeToString(clone);
  const save = (blob, ext) => {
    if (!blob) return;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name + '.' + ext;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };
  if (kind === 'html') {
    const html = '<!doctype html><html><head><meta charset="utf-8"><title>' + name + '</title>' + (fontCss ? '<style>' + fontCss + '</style>' : '') + '</head><body style="margin:0">' + xml + '</body></html>';
    return save(new Blob([html], {
      type: 'text/html'
    }), 'html');
  }

  // PNG: the SVG's own width/height must be the output resolution — an
  // <img>-loaded SVG rasterizes at its intrinsic size, so sizing it at 1×
  // and ctx.scale()-ing up would just upscale a 1× bitmap. viewBox maps the
  // w×h foreignObject onto the px·w × px·h SVG canvas so the browser renders
  // the HTML at full resolution.
  const px = 3;
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + w * px + '" height="' + h * px + '" viewBox="0 0 ' + w + ' ' + h + '"><foreignObject width="' + w + '" height="' + h + '">' + (fontCss ? '<style><![CDATA[' + fontCss + ']]></style>' : '') + xml + '</foreignObject></svg>';
  const img = new Image();
  await new Promise((res, rej) => {
    img.onload = res;
    img.onerror = () => rej(new Error('svg load failed'));
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  });
  const cv = document.createElement('canvas');
  cv.width = w * px;
  cv.height = h * px;
  cv.getContext('2d').drawImage(img, 0, 0);
  cv.toBlob(blob => save(blob, 'png'), 'image/png');
}
function DCArtboardFrame({
  sectionId,
  artboard,
  label,
  order,
  onRename,
  onReorder,
  onFocus,
  onDelete
}) {
  const {
    id: rawId,
    label: rawLabel,
    width = 260,
    height = 480,
    children,
    style = {}
  } = artboard.props;
  const id = rawId ?? rawLabel;
  const ref = React.useRef(null);
  const cardRef = React.useRef(null);
  const menuRef = React.useRef(null);
  const [menuOpen, setMenuOpen] = React.useState(false);
  const [confirming, setConfirming] = React.useState(false);

  // ⋯ menu: close on any outside pointerdown. Two-click delete lives inside
  // the menu — first click arms the row, second commits; closing disarms.
  React.useEffect(() => {
    if (!menuOpen) {
      setConfirming(false);
      return;
    }
    const off = e => {
      if (!menuRef.current || !menuRef.current.contains(e.target)) setMenuOpen(false);
    };
    document.addEventListener('pointerdown', off, true);
    return () => document.removeEventListener('pointerdown', off, true);
  }, [menuOpen]);
  const doExport = kind => {
    setMenuOpen(false);
    if (!cardRef.current) return;
    const name = String(label || id || 'artboard').replace(/[^\w\s.-]+/g, '_');
    dcExport(cardRef.current, width, height, name, kind).catch(e => console.error('[design-canvas] export failed:', e));
  };

  // Live drag-reorder: dragged card sticks to cursor; siblings slide into
  // their would-be slots in real time via transforms. DOM order only
  // changes on drop.
  const onGripDown = e => {
    e.preventDefault();
    e.stopPropagation();
    const me = ref.current;
    // translateX is applied in local (pre-scale) space but pointer deltas and
    // getBoundingClientRect().left are screen-space — divide by the viewport's
    // current scale so the dragged card tracks the cursor at any zoom level.
    const scale = me.getBoundingClientRect().width / me.offsetWidth || 1;
    const peers = Array.from(document.querySelectorAll(`[data-dc-section="${sectionId}"] [data-dc-slot]`));
    const homes = peers.map(el => ({
      el,
      id: el.dataset.dcSlot,
      x: el.getBoundingClientRect().left
    }));
    const slotXs = homes.map(h => h.x);
    const startIdx = order.indexOf(id);
    const startX = e.clientX;
    let liveOrder = order.slice();
    me.classList.add('dc-dragging');
    const layout = () => {
      for (const h of homes) {
        if (h.id === id) continue;
        const slot = liveOrder.indexOf(h.id);
        h.el.style.transform = `translateX(${(slotXs[slot] - h.x) / scale}px)`;
      }
    };
    const move = ev => {
      const dx = ev.clientX - startX;
      me.style.transform = `translateX(${dx / scale}px)`;
      const cur = homes[startIdx].x + dx;
      let nearest = 0,
        best = Infinity;
      for (let i = 0; i < slotXs.length; i++) {
        const d = Math.abs(slotXs[i] - cur);
        if (d < best) {
          best = d;
          nearest = i;
        }
      }
      if (liveOrder.indexOf(id) !== nearest) {
        liveOrder = order.filter(k => k !== id);
        liveOrder.splice(nearest, 0, id);
        layout();
      }
    };
    const up = () => {
      document.removeEventListener('pointermove', move);
      document.removeEventListener('pointerup', up);
      const finalSlot = liveOrder.indexOf(id);
      me.classList.remove('dc-dragging');
      me.style.transform = `translateX(${(slotXs[finalSlot] - homes[startIdx].x) / scale}px)`;
      // After the settle transition, kill transitions + clear transforms +
      // commit the reorder in the same frame so there's no visual snap-back.
      setTimeout(() => {
        for (const h of homes) {
          h.el.style.transition = 'none';
          h.el.style.transform = '';
        }
        if (liveOrder.join('|') !== order.join('|')) onReorder(liveOrder);
        requestAnimationFrame(() => requestAnimationFrame(() => {
          for (const h of homes) h.el.style.transition = '';
        }));
      }, 180);
    };
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', up);
  };
  return /*#__PURE__*/React.createElement("div", {
    ref: ref,
    "data-dc-slot": id,
    style: {
      position: 'relative',
      flexShrink: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "dc-header",
    "data-omelette-chrome": "",
    style: {
      color: DC.label
    },
    onPointerDown: e => e.stopPropagation()
  }, /*#__PURE__*/React.createElement("div", {
    className: "dc-labelrow"
  }, /*#__PURE__*/React.createElement("div", {
    className: "dc-grip",
    onPointerDown: onGripDown,
    title: "Drag to reorder"
  }, /*#__PURE__*/React.createElement("svg", {
    width: "9",
    height: "13",
    viewBox: "0 0 9 13",
    fill: "currentColor"
  }, /*#__PURE__*/React.createElement("circle", {
    cx: "2",
    cy: "2",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "7",
    cy: "2",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "2",
    cy: "6.5",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "7",
    cy: "6.5",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "2",
    cy: "11",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "7",
    cy: "11",
    r: "1.1"
  }))), /*#__PURE__*/React.createElement("div", {
    className: "dc-labeltext",
    onClick: onFocus,
    title: "Click to focus"
  }, /*#__PURE__*/React.createElement(DCEditable, {
    value: label,
    onChange: onRename,
    onClick: e => e.stopPropagation(),
    style: {
      fontSize: 15,
      fontWeight: 500,
      color: DC.label,
      lineHeight: 1
    }
  }))), /*#__PURE__*/React.createElement("div", {
    className: "dc-btns"
  }, /*#__PURE__*/React.createElement("div", {
    ref: menuRef,
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "dc-kebab",
    title: "More",
    onClick: () => setMenuOpen(o => !o)
  }, /*#__PURE__*/React.createElement("svg", {
    width: "12",
    height: "12",
    viewBox: "0 0 12 12",
    fill: "currentColor"
  }, /*#__PURE__*/React.createElement("circle", {
    cx: "2.5",
    cy: "6",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "6",
    cy: "6",
    r: "1.1"
  }), /*#__PURE__*/React.createElement("circle", {
    cx: "9.5",
    cy: "6",
    r: "1.1"
  }))), menuOpen && /*#__PURE__*/React.createElement("div", {
    className: "dc-menu",
    onPointerDown: e => e.stopPropagation()
  }, /*#__PURE__*/React.createElement("button", {
    onClick: () => doExport('png')
  }, "Download PNG"), /*#__PURE__*/React.createElement("button", {
    onClick: () => doExport('html')
  }, "Download HTML"), /*#__PURE__*/React.createElement("hr", null), /*#__PURE__*/React.createElement("button", {
    className: "dc-danger",
    onClick: () => {
      if (confirming) {
        setMenuOpen(false);
        onDelete();
      } else setConfirming(true);
    }
  }, confirming ? 'Click again to delete' : 'Delete'))), /*#__PURE__*/React.createElement("button", {
    className: "dc-expand",
    onClick: onFocus,
    title: "Focus"
  }, /*#__PURE__*/React.createElement("svg", {
    width: "12",
    height: "12",
    viewBox: "0 0 12 12",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.6",
    strokeLinecap: "round"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M7 1h4v4M5 11H1V7M11 1L7.5 4.5M1 11l3.5-3.5"
  }))))), /*#__PURE__*/React.createElement("div", {
    ref: cardRef,
    className: "dc-card",
    style: {
      borderRadius: 2,
      boxShadow: '0 1px 3px rgba(0,0,0,.08),0 4px 16px rgba(0,0,0,.06)',
      overflow: 'hidden',
      width,
      height,
      background: '#fff',
      ...style
    }
  }, children || /*#__PURE__*/React.createElement("div", {
    style: {
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#bbb',
      fontSize: 13,
      fontFamily: DC.font
    }
  }, id)));
}

// Inline rename — commits on blur or Enter.
function DCEditable({
  value,
  onChange,
  style,
  tag = 'span',
  onClick
}) {
  const T = tag;
  return /*#__PURE__*/React.createElement(T, {
    className: "dc-editable",
    contentEditable: true,
    suppressContentEditableWarning: true,
    onClick: onClick,
    onPointerDown: e => e.stopPropagation(),
    onBlur: e => onChange && onChange(e.currentTarget.textContent),
    onKeyDown: e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        e.currentTarget.blur();
      }
    },
    style: style
  }, value);
}

// ─────────────────────────────────────────────────────────────
// Focus mode — overlay one artboard; ←/→ within section, ↑/↓ across
// sections, Esc or backdrop click to exit.
// ─────────────────────────────────────────────────────────────
function DCFocusOverlay({
  entry,
  sectionMeta,
  sectionOrder
}) {
  const ctx = React.useContext(DCCtx);
  const {
    sectionId,
    artboard
  } = entry;
  const sec = ctx.section(sectionId);
  const meta = sectionMeta[sectionId];
  const peers = meta.slotIds;
  const aid = artboard.props.id ?? artboard.props.label;
  const idx = peers.indexOf(aid);
  const secIdx = sectionOrder.indexOf(sectionId);
  const go = d => {
    const n = peers[(idx + d + peers.length) % peers.length];
    if (n) ctx.setFocus(`${sectionId}/${n}`);
  };
  const goSection = d => {
    // Sections whose artboards are all deleted have slotIds:[] — step past
    // them to the next non-empty section so ↑/↓ doesn't dead-end.
    const n = sectionOrder.length;
    for (let i = 1; i < n; i++) {
      const ns = sectionOrder[((secIdx + d * i) % n + n) % n];
      const first = sectionMeta[ns] && sectionMeta[ns].slotIds[0];
      if (first) {
        ctx.setFocus(`${ns}/${first}`);
        return;
      }
    }
  };
  React.useEffect(() => {
    const k = e => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        go(-1);
      }
      if (e.key === 'ArrowRight') {
        e.preventDefault();
        go(1);
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        goSection(-1);
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        goSection(1);
      }
    };
    document.addEventListener('keydown', k);
    return () => document.removeEventListener('keydown', k);
  });
  const {
    width = 260,
    height = 480,
    children
  } = artboard.props;
  const [vp, setVp] = React.useState({
    w: window.innerWidth,
    h: window.innerHeight
  });
  React.useEffect(() => {
    const r = () => setVp({
      w: window.innerWidth,
      h: window.innerHeight
    });
    window.addEventListener('resize', r);
    return () => window.removeEventListener('resize', r);
  }, []);
  const scale = Math.max(0.1, Math.min((vp.w - 200) / width, (vp.h - 260) / height, 2));
  const [ddOpen, setDd] = React.useState(false);
  const Arrow = ({
    dir,
    onClick
  }) => /*#__PURE__*/React.createElement("button", {
    onClick: e => {
      e.stopPropagation();
      onClick();
    },
    style: {
      position: 'absolute',
      top: '50%',
      [dir]: 28,
      transform: 'translateY(-50%)',
      border: 'none',
      background: 'rgba(255,255,255,.08)',
      color: 'rgba(255,255,255,.9)',
      width: 44,
      height: 44,
      borderRadius: 22,
      fontSize: 18,
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'background .15s'
    },
    onMouseEnter: e => e.currentTarget.style.background = 'rgba(255,255,255,.18)',
    onMouseLeave: e => e.currentTarget.style.background = 'rgba(255,255,255,.08)'
  }, /*#__PURE__*/React.createElement("svg", {
    width: "18",
    height: "18",
    viewBox: "0 0 18 18",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "2",
    strokeLinecap: "round"
  }, /*#__PURE__*/React.createElement("path", {
    d: dir === 'left' ? 'M11 3L5 9l6 6' : 'M7 3l6 6-6 6'
  })));

  // Portal to body so position:fixed is the real viewport regardless of any
  // transform on DesignCanvas's ancestors (including the canvas zoom itself).
  return ReactDOM.createPortal(/*#__PURE__*/React.createElement("div", {
    onClick: () => ctx.setFocus(null),
    onWheel: e => e.preventDefault(),
    style: {
      position: 'fixed',
      inset: 0,
      zIndex: 100,
      background: 'rgba(24,20,16,.6)',
      backdropFilter: 'blur(14px)',
      fontFamily: DC.font,
      color: '#fff'
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: e => e.stopPropagation(),
    style: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: 72,
      display: 'flex',
      alignItems: 'flex-start',
      padding: '16px 20px 0',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("button", {
    onClick: () => setDd(o => !o),
    style: {
      border: 'none',
      background: 'transparent',
      color: '#fff',
      cursor: 'pointer',
      padding: '6px 8px',
      borderRadius: 6,
      textAlign: 'left',
      fontFamily: 'inherit'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 18,
      fontWeight: 600,
      letterSpacing: -0.3
    }
  }, meta.title), /*#__PURE__*/React.createElement("svg", {
    width: "11",
    height: "11",
    viewBox: "0 0 11 11",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    style: {
      opacity: .7
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M2 4l3.5 3.5L9 4"
  }))), meta.subtitle && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      fontSize: 13,
      opacity: .6,
      fontWeight: 400,
      marginTop: 2
    }
  }, meta.subtitle)), ddOpen && /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      top: '100%',
      left: 0,
      marginTop: 4,
      background: '#2a251f',
      borderRadius: 8,
      boxShadow: '0 8px 32px rgba(0,0,0,.4)',
      padding: 4,
      minWidth: 200,
      zIndex: 10
    }
  }, sectionOrder.filter(sid => sectionMeta[sid].slotIds.length).map(sid => /*#__PURE__*/React.createElement("button", {
    key: sid,
    onClick: () => {
      setDd(false);
      const f = sectionMeta[sid].slotIds[0];
      if (f) ctx.setFocus(`${sid}/${f}`);
    },
    style: {
      display: 'block',
      width: '100%',
      textAlign: 'left',
      border: 'none',
      cursor: 'pointer',
      background: sid === sectionId ? 'rgba(255,255,255,.1)' : 'transparent',
      color: '#fff',
      padding: '8px 12px',
      borderRadius: 5,
      fontSize: 14,
      fontWeight: sid === sectionId ? 600 : 400,
      fontFamily: 'inherit'
    }
  }, sectionMeta[sid].title)))), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }), /*#__PURE__*/React.createElement("button", {
    onClick: () => ctx.setFocus(null),
    onMouseEnter: e => e.currentTarget.style.background = 'rgba(255,255,255,.12)',
    onMouseLeave: e => e.currentTarget.style.background = 'transparent',
    style: {
      border: 'none',
      background: 'transparent',
      color: 'rgba(255,255,255,.7)',
      width: 32,
      height: 32,
      borderRadius: 16,
      fontSize: 20,
      cursor: 'pointer',
      lineHeight: 1,
      transition: 'background .12s'
    }
  }, "\xD7")), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      top: 64,
      bottom: 56,
      left: 100,
      right: 100,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: e => e.stopPropagation(),
    style: {
      width: width * scale,
      height: height * scale,
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width,
      height,
      transform: `scale(${scale})`,
      transformOrigin: 'top left',
      background: '#fff',
      borderRadius: 2,
      overflow: 'hidden',
      boxShadow: '0 20px 80px rgba(0,0,0,.4)'
    }
  }, children || /*#__PURE__*/React.createElement("div", {
    style: {
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#bbb'
    }
  }, aid))), /*#__PURE__*/React.createElement("div", {
    onClick: e => e.stopPropagation(),
    style: {
      fontSize: 14,
      fontWeight: 500,
      opacity: .85,
      textAlign: 'center'
    }
  }, (sec.labels || {})[aid] ?? artboard.props.label, /*#__PURE__*/React.createElement("span", {
    style: {
      opacity: .5,
      marginLeft: 10,
      fontVariantNumeric: 'tabular-nums'
    }
  }, idx + 1, " / ", peers.length))), /*#__PURE__*/React.createElement(Arrow, {
    dir: "left",
    onClick: () => go(-1)
  }), /*#__PURE__*/React.createElement(Arrow, {
    dir: "right",
    onClick: () => go(1)
  }), /*#__PURE__*/React.createElement("div", {
    onClick: e => e.stopPropagation(),
    style: {
      position: 'absolute',
      bottom: 20,
      left: '50%',
      transform: 'translateX(-50%)',
      display: 'flex',
      gap: 8
    }
  }, peers.map((p, i) => /*#__PURE__*/React.createElement("button", {
    key: p,
    onClick: () => ctx.setFocus(`${sectionId}/${p}`),
    style: {
      border: 'none',
      padding: 0,
      cursor: 'pointer',
      width: 6,
      height: 6,
      borderRadius: 3,
      background: i === idx ? '#fff' : 'rgba(255,255,255,.3)'
    }
  })))), document.body);
}

// ─────────────────────────────────────────────────────────────
// Post-it — absolute-positioned sticky note
// ─────────────────────────────────────────────────────────────
function DCPostIt({
  children,
  top,
  left,
  right,
  bottom,
  rotate = -2,
  width = 180
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      top,
      left,
      right,
      bottom,
      width,
      background: DC.postitBg,
      padding: '14px 16px',
      fontFamily: '"Comic Sans MS", "Marker Felt", "Segoe Print", cursive',
      fontSize: 14,
      lineHeight: 1.4,
      color: DC.postitText,
      boxShadow: '0 2px 8px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08)',
      transform: `rotate(${rotate}deg)`,
      zIndex: 5
    }
  }, children);
}
Object.assign(window, {
  DesignCanvas,
  DCSection,
  DCArtboard,
  DCPostIt
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/explore/design-canvas.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/explore/week-data.jsx
try { (() => {
// Real Week-in-Review data, grouped from the IBM webMethods MFT/IWHI Slack threads.
// Week of Jun 2–8, 2026.
window.WEEK_DATA = {
  weekLabel: 'Jun 2 – 8, 2026',
  totalThisWeek: 22,
  totalLastWeek: 18,
  deltaPct: +18,
  // vs last week
  newQuestionTypes: 5,
  // groups that didn't appear last week
  groupsThisWeek: 8,
  answered: 3,
  // 6-week volume trend (oldest → newest), newest = this week
  trend: [14, 12, 19, 16, 18, 22],
  // movement: 'new' | number (rank change vs last week, + = rose)
  groups: [{
    rank: 1,
    count: 4,
    similarity: '90%',
    movement: 'new',
    topic: 'Antivirus scanning',
    question: 'How do I configure virus scanning in MFT and handle failures?',
    keywords: ['mft', 'antivirus', 'quarantine', 'notification'],
    questions: [{
      text: 'Copy Task to target failing: "Exception while scanning for virus" — please advise.',
      date: 'Jun 5'
    }, {
      text: 'When a virus is detected, how can we send an email notification to an admin?',
      date: 'Jun 5'
    }, {
      text: 'Post-processing virus scanner → move file to quarantine or approved folder + send mail?',
      date: 'Jun 2'
    }, {
      text: 'Can a post-processing script return a custom error to drive quarantine vs approve?',
      date: 'Jun 2'
    }]
  }, {
    rank: 2,
    count: 3,
    similarity: '88%',
    movement: 'new',
    topic: 'Metering & usage stats',
    question: 'How can customers measure MFT transaction statistics without the metering server?',
    keywords: ['metering', 'transactions', 'usage', 'entitlements'],
    questions: [{
      text: 'How to check own transaction stats (inbound/outbound counts, file sizes) beyond metering reports?',
      date: 'May 30'
    }, {
      text: 'In the absence of a metering server, how can a customer estimate MFT transactions?',
      date: 'Jun 2'
    }, {
      text: 'Does the wM Metering Agent come pre-installed with the Capabilities Container images for MFT?',
      date: 'Jun 9'
    }]
  }, {
    rank: 3,
    count: 2,
    similarity: '86%',
    movement: +2,
    topic: 'Scheduled Action APIs',
    question: 'Is there a REST API to trigger or deactivate Scheduled Actions?',
    keywords: ['rest-api', 'scheduled-actions', 'automation'],
    questions: [{
      text: 'Is there a REST API to deactivate a list of Scheduled and Post-Processing Actions?',
      date: 'Jun 5'
    }, {
      text: 'Can we trigger a file transfer via a REST API call instead of a scheduled action?',
      date: 'Jun 3'
    }]
  }, {
    rank: 4,
    count: 2,
    similarity: '84%',
    movement: 'new',
    topic: 'MFT UI errors after upgrade',
    question: 'Internal error / NullPointerException opening the MFT UI after a 12.x install',
    keywords: ['mft-ui', 'upgrade', 'error', 'nullpointer'],
    questions: [{
      text: 'Just installed v12, cannot open MFT UI — MFTServiceException "internal error".',
      date: 'Jun 3'
    }, {
      text: 'Debug log: NullPointerException — Datastore.logger is null while fetching UI settings.',
      date: 'Jun 3'
    }]
  }, {
    rank: 5,
    count: 1,
    similarity: '—',
    movement: -1,
    topic: 'Azure Blob auth',
    question: 'Azure Blob Container-level SAS token authorization failure',
    keywords: ['azure', 'sas-token', 'authorization'],
    questions: [{
      text: 'Storage-account token works but Container-level SAS token fails authorization — do we support it?',
      date: 'Jun 5'
    }]
  }, {
    rank: 6,
    count: 1,
    similarity: '—',
    movement: 'new',
    topic: 'Control-file triggers',
    question: 'Use a control (.ctrl) file to trigger transfer once the data file is ready',
    keywords: ['find-task', 'control-file', 'trigger'],
    questions: [{
      text: 'On finding {name}.ctrl, move {name}.dat to the destination — can Find/Move tasks do this?',
      date: 'Jun 5'
    }]
  }, {
    rank: 7,
    count: 1,
    similarity: '—',
    movement: -3,
    topic: 'Monitoring & alerting',
    question: 'IWHI end-to-end monitoring & alerting best practices',
    keywords: ['iwhi', 'monitoring', 'alerting'],
    questions: [{
      text: 'Best way to monitor a single app and alert on the first error — one group per B2B/IS/MFT?',
      date: 'Jun 9'
    }]
  }, {
    rank: 8,
    count: 1,
    similarity: '—',
    movement: +1,
    topic: 'Thread exhaustion',
    question: 'Avoiding thread exhaustion with thousands of scheduled actions',
    keywords: ['threads', 'scheduler', 'scaling'],
    questions: [{
      text: '8,600 scheduled actions on a 2-node cluster — how to avoid running out of threads?',
      date: 'Jun 5'
    }]
  }]
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/explore/week-data.jsx", error: String((e && e.message) || e) }); }

// ui_kits/analyzer/explore/wir-shared.jsx
try { (() => {
// Shared chrome + small primitives for the Week-in-Review explorations.
const DS_NS = () => window.QuestionAnalyzerDesignSystem_03a921;

// App shell header with the Dashboard | Week in Review segmented toggle,
// the always-available upload button, and the account avatar.
function AppShellHeader({
  active = 'week'
}) {
  const seg = (label, key) => ({
    height: 32,
    padding: '0 16px',
    display: 'inline-flex',
    alignItems: 'center',
    fontSize: 13,
    cursor: 'pointer',
    border: 'none',
    background: active === key ? 'var(--blue-60)' : 'transparent',
    color: active === key ? '#fff' : 'var(--gray-30)'
  });
  return /*#__PURE__*/React.createElement("header", {
    style: {
      height: 48,
      background: 'var(--gray-100)',
      color: '#fff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 16px',
      flex: '0 0 auto'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 26,
      height: 26,
      background: '#fff',
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 5,
      top: 6,
      width: 15,
      height: 3,
      background: 'var(--blue-60)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 5,
      top: 12,
      width: 10,
      height: 3,
      background: 'var(--blue-50)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 5,
      top: 18,
      width: 6,
      height: 3,
      background: 'var(--blue-40)'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14
    }
  }, /*#__PURE__*/React.createElement("b", {
    style: {
      fontWeight: 600
    }
  }, "Question"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 300,
      opacity: .8
    }
  }, " Analyzer")), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      border: '1px solid var(--gray-80)',
      marginLeft: 8
    }
  }, /*#__PURE__*/React.createElement("button", {
    style: seg('Dashboard', 'dashboard')
  }, "Dashboard"), /*#__PURE__*/React.createElement("button", {
    style: seg('Week in Review', 'week')
  }, "Week in Review"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("button", {
    style: {
      height: 32,
      padding: '0 14px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: 8,
      background: 'transparent',
      color: '#fff',
      border: '1px solid var(--gray-70)',
      fontSize: 13,
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "upload",
    size: 15
  }), " Upload transcript"), /*#__PURE__*/React.createElement("span", {
    style: {
      width: 30,
      height: 30,
      borderRadius: '50%',
      background: 'var(--blue-60)',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 12,
      fontWeight: 600,
      border: '2px solid var(--gray-80)'
    }
  }, "SA")));
}

// ▲18% / ▼6% delta chip
function DeltaBadge({
  value,
  size = 'md'
}) {
  const up = value >= 0;
  const big = size === 'lg';
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 4,
      color: up ? 'var(--green-60)' : 'var(--red-60)',
      fontFamily: 'var(--font-mono)',
      fontSize: big ? 18 : 13,
      fontWeight: 500
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: up ? 'trending-up' : 'trending-down',
    size: big ? 18 : 14
  }), up ? '+' : '', value, "%");
}

// NEW / ▲2 / ▼1 movement marker for a ranked row
function MovementBadge({
  movement
}) {
  if (movement === 'new') {
    return /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 10,
        letterSpacing: '.5px',
        color: 'var(--blue-70)',
        background: 'var(--blue-20)',
        padding: '2px 6px',
        borderRadius: 'var(--radius-sm)'
      }
    }, "NEW");
  }
  if (typeof movement === 'number' && movement !== 0) {
    const up = movement > 0;
    return /*#__PURE__*/React.createElement("span", {
      style: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: 2,
        fontFamily: 'var(--font-mono)',
        fontSize: 11,
        color: up ? 'var(--green-60)' : 'var(--gray-50)'
      }
    }, /*#__PURE__*/React.createElement(Icon, {
      name: up ? 'arrow-up' : 'arrow-down',
      size: 12
    }), Math.abs(movement));
  }
  return /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-mono)',
      fontSize: 11,
      color: 'var(--text-placeholder)'
    }
  }, "\u2014");
}

// Tiny vertical bar-chart of weekly volume; last bar highlighted.
function TrendBars({
  data,
  height = 64,
  barW = 20,
  gap = 8
}) {
  const max = Math.max(...data);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-end',
      gap,
      height
    }
  }, data.map((v, i) => {
    const last = i === data.length - 1;
    return /*#__PURE__*/React.createElement("div", {
      key: i,
      style: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 4
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        width: barW,
        height: Math.max(3, v / max * (height - 16)),
        background: last ? 'var(--blue-60)' : 'var(--gray-30)'
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        fontFamily: 'var(--font-mono)',
        fontSize: 9,
        color: last ? 'var(--text-primary)' : 'var(--text-placeholder)'
      }
    }, v));
  }));
}
Object.assign(window, {
  DS_NS,
  AppShellHeader,
  DeltaBadge,
  MovementBadge,
  TrendBars
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/analyzer/explore/wir-shared.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.FileDropzone = __ds_scope.FileDropzone;

__ds_ns.MetricTile = __ds_scope.MetricTile;

__ds_ns.QuestionGroup = __ds_scope.QuestionGroup;

__ds_ns.Slider = __ds_scope.Slider;

__ds_ns.Tag = __ds_scope.Tag;

})();
