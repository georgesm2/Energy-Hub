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
    <h3>Carbon Intensity gCO2 / kWh</h3>
    <div class="chart-area">
        <Chart {init} options={options} />
    </div>
</div>

<style>
    .card {
        background-color: #fff;
        border-radius: 10px;
        min-width: 0;
        box-sizing: border-box;
        text-align: center;
    }
    .chart-area {
        height: 26rem;
        width: 100%;
        overflow: hidden;
    }
    @media (max-width: 610px) {
        .chart-area { height: 25rem; }
    }
</style>