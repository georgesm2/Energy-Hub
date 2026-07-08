<script>
    import { Chart } from 'svelte-echarts';
    import { init, use } from 'echarts/core';
    import { LineChart } from 'echarts/charts';
    import { ToolboxComponent, DataZoomComponent, GridComponent, TooltipComponent } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';
    
    // now with tree-shaking
    use([LineChart, ToolboxComponent, DataZoomComponent, GridComponent, CanvasRenderer, TooltipComponent])


    // Accept only the unified options object via Svelte 5 props
    let { options } = $props();
</script>

<div class="card chart" id="carbon-intensity-chart">
    <h3>Interconnector Flows / GW</h3>
    <div class="chart-area">
        <Chart {init} options={options} />
    </div>
</div>

<style>
    .card {
        border: 1px #abc solid;
    }
</style>