<template>
  <div class="application-canvas">
    <div ref="canvasWrapper" class="application-canvas__wrapper"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import LogicFlow, { GraphConfigData, RectNode, RectNodeModel, h } from '@logicflow/core'
import '@logicflow/core/dist/style/index.css'

import {
  CanvasEdgeData,
  CanvasNodeData,
  CanvasNodeType,
  DEFAULT_NODE_HEIGHT,
  DEFAULT_NODE_WIDTH,
} from './ApplicationCanvas/types'

const props = withDefaults(
  defineProps<{
    nodes: CanvasNodeData[]
    edges: CanvasEdgeData[]
    readonly?: boolean
  }>(),
  {
    nodes: () => [],
    edges: () => [],
    readonly: false
  }
)

const emit = defineEmits<{
  'canvas:ready': [LogicFlow]
  'node:click': [CanvasNodeData]
  'edge:click': [CanvasEdgeData]
  'node:moved': [CanvasNodeData]
  'node:removed': [CanvasNodeData]
  'edge:added': [CanvasEdgeData]
  'edge:removed': [CanvasEdgeData]
  'blank:click': []
}>()

const canvasWrapper = ref<HTMLDivElement | null>(null)
let lf: LogicFlow | null = null
const registeredInstances = new WeakSet<LogicFlow>()
let isInternalDrag = false

const TYPE_COLOR_MAP: Record<CanvasNodeType, string> = {
  [CanvasNodeType.HOST]: '#2563eb',
  [CanvasNodeType.NETWORK]: '#0ea5e9',
  [CanvasNodeType.STORAGE]: '#a855f7',
  [CanvasNodeType.OBJECT_STORAGE]: '#f97316',
  [CanvasNodeType.DATABASE]: '#ef4444',
  [CanvasNodeType.SERVICE]: '#6366f1',
  [CanvasNodeType.CUSTOM]: '#0f172a',
}

const TYPE_TINT_MAP: Record<CanvasNodeType, string> = {
  [CanvasNodeType.HOST]: '#eef2ff',
  [CanvasNodeType.NETWORK]: '#f0f9ff',
  [CanvasNodeType.STORAGE]: '#faf5ff',
  [CanvasNodeType.OBJECT_STORAGE]: '#fff7ed',
  [CanvasNodeType.DATABASE]: '#fef2f2',
  [CanvasNodeType.SERVICE]: '#eef2ff',
  [CanvasNodeType.CUSTOM]: '#f8fafc',
}

const initCanvas = () => {
  if (!canvasWrapper.value) return

  lf = new LogicFlow({
    container: canvasWrapper.value,
    isSilentMode: props.readonly,
    grid: {
      visible: true,
      type: 'mesh',
      size: 20
    },
    keyboard: {
      enabled: false
    }
  })

  registerCustomNodes(lf)
  lf.updateEditConfig({
    isSilentMode: props.readonly,
    // Allow background drag for panning while nodes remain draggable individually
    stopMoveGraph: false,
    nodeDraggable: !props.readonly,
    edgeDraggable: !props.readonly,
    adjustNodePosition: true,
  })
  renderGraph()
  attachEventHandlers()
  emit('canvas:ready', lf)
}

const renderGraph = () => {
  if (!lf) return
  const data: GraphConfigData = {
    nodes: props.nodes.map((node) => ({
      id: String(node.id),
      type: 'device-node',
      x: node.x,
      y: node.y,
      text: node.label,
      properties: {
        label: node.label,
        icon: node.icon,
        color: node.color,
        bindingHostId: node.bindingHostId,
        status: node.status,
        data: node.data || {},
        rawType: node.type,
      },
    })),
    edges: props.edges.map((edge) => ({
      id: edge.id ? String(edge.id) : undefined,
      type: 'polyline',
      sourceNodeId: String(edge.source),
      targetNodeId: String(edge.target),
      text: edge.label || edge.relationshipType,
      properties: {
        relationshipType: edge.relationshipType,
        description: edge.description,
        data: edge.data || {},
      },
    })),
  }
  lf.render(data)
}

const registerCustomNodes = (instance: LogicFlow) => {
  if (registeredInstances.has(instance)) {
    return
  }

  const createIconNodes = (type: CanvasNodeType, cx: number, cy: number, stroke: string) => {
    const nodes: any[] = []
    const strokeWidth = 1.5
    const cap = 'round'
    const join = 'round'

    switch (type) {
      case CanvasNodeType.HOST:
        nodes.push(
          h('rect', {
            x: cx - 9,
            y: cy - 6,
            width: 18,
            height: 12,
            rx: 2,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
            'stroke-linejoin': join,
            fill: 'none',
          }),
          h('line', {
            x1: cx - 6,
            y1: cy + 6,
            x2: cx + 6,
            y2: cy + 6,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          }),
          h('line', {
            x1: cx - 3,
            y1: cy + 6,
            x2: cx - 3,
            y2: cy + 9,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          }),
          h('line', {
            x1: cx + 3,
            y1: cy + 6,
            x2: cx + 3,
            y2: cy + 9,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          })
        )
        break
      case CanvasNodeType.NETWORK:
        nodes.push(
          h('circle', {
            cx,
            cy,
            r: 5,
            stroke,
            'stroke-width': strokeWidth,
            fill: 'none',
          }),
          h('circle', { cx: cx - 9, cy: cy - 9, r: 2, fill: stroke }),
          h('line', {
            x1: cx - 9,
            y1: cy - 9,
            x2: cx - 3,
            y2: cy - 1,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          }),
          h('circle', { cx: cx + 9, cy: cy - 4, r: 2, fill: stroke }),
          h('line', {
            x1: cx + 9,
            y1: cy - 4,
            x2: cx + 2,
            y2: cy - 1,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          }),
          h('circle', { cx: cx - 4, cy: cy + 9, r: 2, fill: stroke }),
          h('line', {
            x1: cx - 4,
            y1: cy + 9,
            x2: cx - 1,
            y2: cy + 2,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          })
        )
        break
      case CanvasNodeType.STORAGE:
        nodes.push(
          h('ellipse', {
            cx,
            cy: cy - 3,
            rx: 9,
            ry: 5,
            stroke,
            'stroke-width': strokeWidth,
            fill: 'none',
          }),
          h('path', {
            d: `M${cx - 9} ${cy - 3}v8c0 3.2 18 3.2 18 0v-8`,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
            'stroke-linejoin': join,
            fill: 'none',
          }),
          h('ellipse', {
            cx,
            cy: cy + 5,
            rx: 9,
            ry: 5,
            stroke,
            'stroke-width': strokeWidth,
            fill: 'none',
          })
        )
        break
      case CanvasNodeType.OBJECT_STORAGE:
        nodes.push(
          h('path', {
            d: `M${cx - 8} ${cy + 2}c0-4 3.5-7 7.5-7 3 0 5.6 1.7 6.8 4.1 1.9 0.2 3.7 1.5 4.2 3.6 0.6 2.4-0.9 4.8-3.3 5.4a4.5 4.5 0 0 1-1.1 0.1h-14.6c-2.1 0-3.9-1.6-4.2-3.7-.3-2 1.1-3.9 3.1-4.5Z`,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
            'stroke-linejoin': join,
            fill: 'none',
          }),
          h('line', {
            x1: cx - 2,
            y1: cy + 6,
            x2: cx + 4,
            y2: cy,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          }),
          h('line', {
            x1: cx + 4,
            y1: cy + 6,
            x2: cx + 8,
            y2: cy + 2,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          })
        )
        break
      case CanvasNodeType.DATABASE:
        nodes.push(
          h('ellipse', {
            cx,
            cy: cy - 4,
            rx: 9,
            ry: 5,
            stroke,
            'stroke-width': strokeWidth,
            fill: 'none',
          }),
          h('path', {
            d: `M${cx - 9} ${cy - 4}v10c0 3.2 18 3.2 18 0v-10`,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
            'stroke-linejoin': join,
            fill: 'none',
          }),
          h('ellipse', {
            cx,
            cy: cy + 6,
            rx: 9,
            ry: 5,
            stroke,
            'stroke-width': strokeWidth,
            fill: 'none',
          }),
          h('line', {
            x1: cx - 9,
            y1: cy,
            x2: cx + 9,
            y2: cy,
            stroke,
            'stroke-width': strokeWidth,
          })
        )
        break
      case CanvasNodeType.SERVICE:
        nodes.push(
          h('polygon', {
            points: `${cx},${cy - 9} ${cx + 7.8},${cy - 4.5} ${cx + 7.8},${cy + 4.5} ${cx},${cy + 9} ${cx - 7.8},${cy + 4.5} ${cx - 7.8},${cy - 4.5}`,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linejoin': join,
            fill: 'none',
          }),
          h('line', {
            x1: cx,
            y1: cy - 6,
            x2: cx,
            y2: cy + 6,
            stroke,
            'stroke-width': strokeWidth,
          }),
          h('line', {
            x1: cx - 4,
            y1: cy,
            x2: cx + 4,
            y2: cy,
            stroke,
            'stroke-width': strokeWidth,
          })
        )
        break
      default:
        nodes.push(
          h('circle', {
            cx,
            cy,
            r: 6,
            stroke,
            'stroke-width': strokeWidth,
            fill: 'none',
          }),
          h('line', {
            x1: cx,
            y1: cy - 4,
            x2: cx,
            y2: cy + 4,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          }),
          h('line', {
            x1: cx - 4,
            y1: cy,
            x2: cx + 4,
            y2: cy,
            stroke,
            'stroke-width': strokeWidth,
            'stroke-linecap': cap,
          })
        )
    }
    return nodes
  }

  class DeviceNodeModel extends RectNodeModel {
    setAttributes() {
      const self = this as any
      if (typeof super.setAttributes === 'function') {
        super.setAttributes()
      }
      self.width = DEFAULT_NODE_WIDTH
      self.height = DEFAULT_NODE_HEIGHT
      if (self.text) {
        self.text.editable = false
      }
      self.draggable = true
    }

    getDefaultAnchor() {
      const self = this as any
      const { x, y, width, height } = self
      const halfW = width / 2
      const halfH = height / 2
      return [
        { x, y: y - halfH, id: `${self.id}_top`, type: 'top' },
        { x: x + halfW, y, id: `${self.id}_right`, type: 'right' },
        { x, y: y + halfH, id: `${self.id}_bottom`, type: 'bottom' },
        { x: x - halfW, y, id: `${self.id}_left`, type: 'left' },
        { x: x + halfW * 0.7, y: y - halfH * 0.7, id: `${self.id}_top_right`, type: 'top-right' },
        { x: x + halfW * 0.7, y: y + halfH * 0.7, id: `${self.id}_bottom_right`, type: 'bottom-right' },
        { x: x - halfW * 0.7, y: y + halfH * 0.7, id: `${self.id}_bottom_left`, type: 'bottom-left' },
        { x: x - halfW * 0.7, y: y - halfH * 0.7, id: `${self.id}_top_left`, type: 'top-left' },
      ]
    }

    getAnchors() {
      return this.getDefaultAnchor()
    }
  }

  class DeviceNodeView extends RectNode {
    getShape() {
      const { model } = (this as any).props
      const { x, y, width, height } = model
      const properties = typeof (model as any).getProperties === 'function'
        ? (model as any).getProperties()
        : (model as any).properties || {}
      const rawType = (properties.rawType as CanvasNodeType) || CanvasNodeType.CUSTOM
      const nodeColor = properties.color || TYPE_COLOR_MAP[rawType] || '#2563eb'
      const hostData = properties.data || {}
      const hostname = hostData.hostname || hostData.name || ''
      const ip = hostData.ip || hostData.ip_address || ''
      const primaryLabel =
        properties.label ||
        model.getText()?.value ||
        hostname ||
        ip ||
        'Resource'
      const secondaryLabel =
        ip && ip !== primaryLabel ? ip : (hostData.vendor || '')
      const status = properties.status || hostData.device_type || hostData.os_type || ''
      const radius = Math.min(width, height) / 2
      const outerRadius = radius
      const innerRadius = radius * 0.78
      const labelY = y + innerRadius + 20
      const secondaryY = labelY + 16
      const statusY = secondaryLabel ? secondaryY + 16 : labelY + 16
      const tintColor = TYPE_TINT_MAP[rawType] || '#f8fafc'

      const tooltipLines = [primaryLabel]
      if (secondaryLabel && secondaryLabel !== primaryLabel) {
        tooltipLines.push(secondaryLabel)
      }
      if (status && status !== primaryLabel && status !== secondaryLabel) {
        tooltipLines.push(status)
      }
      const titleNode = tooltipLines.length > 0 ? h('title', {}, tooltipLines.join('\n')) : null

      const highlightCircle = h('circle', {
        cx: x,
        cy: y,
        r: outerRadius,
        fill: '#ffffff',
        stroke: '#e2e8f0',
        'stroke-width': 1.5,
      })

      const headerClip = h('circle', {
        cx: x,
        cy: y,
        r: innerRadius + 6,
        fill: tintColor,
        opacity: 0.9,
      })

      const innerCircle = h('circle', {
        cx: x,
        cy: y,
        r: innerRadius,
        fill: '#ffffff',
        stroke: '#ffffff',
        'stroke-width': 4,
      })

      const iconCircle = h('circle', {
        cx: x,
        cy: y,
        r: innerRadius * 0.88,
        fill: nodeColor,
        opacity: 0.96,
      })

      const iconNodes = createIconNodes(rawType, x, y, '#ffffff')

      const labelText = h('text', {
        x,
        y: labelY,
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        'font-size': 14,
        fill: '#0f172a',
        'font-family': 'Inter, sans-serif',
        'font-weight': 600,
      }, primaryLabel)

      const secondaryText = secondaryLabel
        ? h('text', {
            x,
            y: secondaryY,
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
            'font-size': 12,
            fill: '#4b5563',
            'font-family': 'Inter, sans-serif',
          }, secondaryLabel)
        : null

      const statusText = status
        ? (() => {
            const paddingX = 16
            const paddingY = 8
            const approximateWidth = Math.max(status.length * 7 + paddingX * 2, 80)
            const badgeX = x - approximateWidth / 2
            const badgeY = statusY - paddingY
            return h('g', {}, [
              h('rect', {
                x: badgeX,
                y: badgeY,
                width: approximateWidth,
                height: paddingY * 2,
                rx: 999,
                ry: 999,
                fill: '#f1f5f9',
              }),
              h('text', {
                x,
                y: statusY,
                'text-anchor': 'middle',
                'dominant-baseline': 'middle',
                'font-size': 12,
                fill: '#475569',
                'font-family': 'Inter, sans-serif',
                'font-weight': 500,
              }, status)
            ])
          })()
        : null

      return h('g', { className: 'application-device-node' }, [
        highlightCircle,
        headerClip,
        innerCircle,
        iconCircle,
        ...iconNodes,
        labelText,
        secondaryText,
        statusText,
        titleNode,
      ].filter(Boolean))
    }
  }

  instance.register({
    type: 'device-node',
    view: DeviceNodeView,
    model: DeviceNodeModel,
  })
  registeredInstances.add(instance)
}

onMounted(() => {
  nextTick(() => initCanvas())
})

onBeforeUnmount(() => {
  if (lf) {
    try {
      lf.graphModel?.clearData?.()
    } catch (error) {
      console.warn('Failed to cleanup LogicFlow instance', error)
    }
    lf = null
  }
})

watch(
  () => [props.nodes, props.edges, props.readonly],
  () => {
    if (!lf) {
      nextTick(() => initCanvas())
      return
    }
    if (isInternalDrag) {
      return
    }
    lf.updateEditConfig({
      isSilentMode: props.readonly,
      stopMoveGraph: false,
      nodeDraggable: !props.readonly,
      edgeDraggable: !props.readonly,
      adjustNodePosition: true,
    })
    renderGraph()
  },
  { deep: true, flush: 'post' }
)

const attachEventHandlers = () => {
  if (!lf) return

  lf.on('node:click', ({ data }: { data: any }) => {
    const node = mapLfNodeToCanvasNode(data)
    emit('node:click', node)
  })

  lf.on('edge:click', ({ data }: { data: any }) => {
    const edge = mapLfEdgeToCanvasEdge(data)
    emit('edge:click', edge)
  })

  lf.on('node:mousemove', ({ data }: { data: any }) => {
    isInternalDrag = true
    const node = mapLfNodeToCanvasNode(data)
    emit('node:moved', node)
    requestAnimationFrame(() => {
      isInternalDrag = false
    })
  })

  lf.on('edge:add', ({ data }: { data: any }) => {
    const edge = mapLfEdgeToCanvasEdge(data)
    emit('edge:added', edge)
  })

  lf.on('edge:delete', ({ data }: { data: any }) => {
    const edge = mapLfEdgeToCanvasEdge(data)
    emit('edge:removed', edge)
  })

  lf.on('blank:click', () => {
    emit('blank:click')
  })

  lf.on('node:delete', ({ data }: { data: any }) => {
    const node = mapLfNodeToCanvasNode(data)
    emit('node:removed', node)
  })
}

const mapLfNodeToCanvasNode = (node: any): CanvasNodeData => {
  const properties = node.properties || {}
  return {
    id: node.id,
    type: properties.rawType || CanvasNodeType.CUSTOM,
    x: node.x,
    y: node.y,
    label: properties.label || node.text?.value || '',
    icon: properties.icon,
    color: properties.color,
    bindingHostId: properties.bindingHostId,
    status: properties.status,
    data: properties.data || {},
  }
}

const mapLfEdgeToCanvasEdge = (edge: any): CanvasEdgeData => {
  const properties = edge.properties || {}
  return {
    id: edge.id,
    source: edge.sourceNodeId,
    target: edge.targetNodeId,
    relationshipType: properties.relationshipType,
    label: edge.text?.value || properties.relationshipType || '',
    description: properties.description,
    data: properties.data || {},
  }
}

const addNode = (node: CanvasNodeData) => {
  if (!lf) return
  lf.addNode({
    id: String(node.id),
    type: 'device-node',
    x: node.x,
    y: node.y,
    text: node.label,
    properties: {
      label: node.label,
      icon: node.icon,
      color: node.color,
      bindingHostId: node.bindingHostId,
      status: node.status,
      data: node.data || {},
      rawType: node.type,
    },
  })
}

const addEdge = (edge: CanvasEdgeData) => {
  if (!lf) return
  lf.addEdge({
    id: edge.id ? String(edge.id) : undefined,
    type: 'polyline',
    sourceNodeId: String(edge.source),
    targetNodeId: String(edge.target),
    text: edge.label || edge.relationshipType,
    properties: {
      relationshipType: edge.relationshipType,
      description: edge.description,
      data: edge.data || {},
    },
  })
}

const removeNode = (id: string | number) => {
  if (!lf) return
  lf.deleteNode(String(id))
}

const removeEdge = (id: string | number) => {
  if (!lf) return
  lf.deleteEdge(String(id))
}

const clear = () => {
  lf?.clearData()
}

defineExpose({
  addNode,
  addEdge,
  removeNode,
  removeEdge,
  clear,
  getLogicFlow: () => lf,
})

</script>

<style scoped>
.application-canvas {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.application-canvas__wrapper {
  flex: 1;
  min-height: 400px;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #ffffff;
}
</style>

