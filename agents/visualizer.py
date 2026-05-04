"""
Visualization Agent
Creates charts and graphs from clinical metrics
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

class VisualizationAgent:

    def __init__(self, metrics, data):
        self.metrics = metrics
        self.data = data

    def _val(self, metric_key, subkey='value', default=0):
        """Safe metric accessor that never raises KeyError."""
        return self.metrics.get(metric_key, {}).get(subkey, default)

    def _status_color(self, metric_key, good_statuses, bad_color='red', warn_color='yellow', good_color='green'):
        status = self.metrics.get(metric_key, {}).get('status', '')
        if status in good_statuses:
            return good_color
        if status in ('critical', 'unknown'):
            return bad_color
        return warn_color

    def create_kpi_summary_chart(self):
        print("📊 Creating KPI Summary Chart...")

        kpi_defs = [
            ("30-Day Readmission (%)",  'readmission_rate',  ['good']),
            ("HAI Rate (per 1000)",     'infection_rate',    ['excellent']),
            ("Mortality Rate (%)",      'mortality_rate',    ['good']),
            ("Avg Length of Stay (d)",  'alos',              ['efficient']),
            ("Bed Turnover Rate",       'bed_turnover',      ['excellent']),
            ("Wait Time (min)",         'wait_time',         ['good']),
            ("No-Show Rate (%)",        'no_show_rate',      ['good']),
            ("Claim Denial Rate (%)",   'denial_rate',       ['good']),
            ("Days in A/R",             'days_in_ar',        ['good']),
            ("Collection Rate (%)",     'collection_rate',   ['excellent']),
            ("Patient Satisfaction",    'satisfaction',      ['excellent']),
        ]

        kpi_names, actual_values, benchmark_values, colors = [], [], [], []

        for label, key, good_statuses in kpi_defs:
            actual = self._val(key, 'value', 0)
            bench  = self._val(key, 'benchmark', 0)
            if actual is None:
                actual = 0
            if bench is None:
                bench = 0
            kpi_names.append(label)
            actual_values.append(actual)
            benchmark_values.append(bench)
            colors.append(self._status_color(key, good_statuses))

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=kpi_names, x=benchmark_values, name='Benchmark',
            orientation='h', marker=dict(color='lightgray'),
            text=[f'{v:.1f}' for v in benchmark_values], textposition='outside',
        ))
        fig.add_trace(go.Bar(
            y=kpi_names, x=actual_values, name='Actual',
            orientation='h', marker=dict(color=colors),
            text=[f'{v:.1f}' for v in actual_values], textposition='outside',
        ))
        fig.update_layout(
            title='Hospital KPI Performance vs. Benchmarks',
            xaxis_title='Value', yaxis_title='Metric',
            barmode='overlay', height=600,
            showlegend=True, template='plotly_white',
        )
        return fig

    def create_department_performance_chart(self):
        print("🏥 Creating Department Performance Chart...")

        patients    = self.data.get('patients', pd.DataFrame())
        readmissions = self.data.get('readmissions', pd.DataFrame())
        infections  = self.data.get('infections', pd.DataFrame())

        dept_admissions = patients['department'].value_counts() if len(patients) else pd.Series(dtype=int)

        if len(readmissions) and len(patients):
            readmit_ids  = readmissions['patient_id'].unique()
            readmit_dept = patients[patients['patient_id'].isin(readmit_ids)]['department'].value_counts()
        else:
            readmit_dept = pd.Series(dtype=int)

        infection_dept = infections['department'].value_counts() if len(infections) else pd.Series(dtype=int)

        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Admissions by Dept', 'Readmissions by Dept', 'Infections by Dept'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]],
        )
        fig.add_trace(go.Bar(x=dept_admissions.index, y=dept_admissions.values,
                             marker_color='steelblue', name='Admissions'), row=1, col=1)
        fig.add_trace(go.Bar(x=readmit_dept.index, y=readmit_dept.values,
                             marker_color='orange', name='Readmissions'), row=1, col=2)
        fig.add_trace(go.Bar(x=infection_dept.index, y=infection_dept.values,
                             marker_color='red', name='Infections'), row=1, col=3)
        fig.update_layout(title_text='Department Performance Breakdown',
                          showlegend=False, height=400, template='plotly_white')
        fig.update_xaxes(tickangle=45)
        return fig

    def create_financial_overview_chart(self):
        print("💰 Creating Financial Overview Chart...")

        claims = self.data.get('claims', pd.DataFrame())
        if len(claims) == 0:
            fig = go.Figure()
            fig.update_layout(title='No claims data available')
            return fig

        claim_status  = claims['claim_status'].value_counts()
        denied_claims = claims[claims['claim_status'] == 'denied']
        denial_reasons = denied_claims['denial_reason'].value_counts() if len(denied_claims) else pd.Series(dtype=int)

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Claim Status', 'Top Denial Reasons'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}]],
        )
        color_map = {'paid': 'green', 'denied': 'red', 'pending': 'yellow'}
        pie_colors = [color_map.get(s, 'gray') for s in claim_status.index]

        fig.add_trace(go.Pie(labels=claim_status.index, values=claim_status.values,
                             marker=dict(colors=pie_colors)), row=1, col=1)
        if len(denial_reasons):
            fig.add_trace(go.Bar(x=denial_reasons.index, y=denial_reasons.values,
                                 marker_color='crimson'), row=1, col=2)
        fig.update_layout(title_text='Financial Performance Overview',
                          showlegend=True, height=400, template='plotly_white')
        fig.update_xaxes(tickangle=45, row=1, col=2)
        return fig

    def create_patient_satisfaction_chart(self):
        print("😊 Creating Patient Satisfaction Chart...")

        surveys = self.data.get('surveys', pd.DataFrame())
        if len(surveys) == 0:
            fig = go.Figure()
            fig.update_layout(title='No survey data available')
            return fig

        satisfaction_scores = surveys['overall_satisfaction']
        benchmark = self._val('satisfaction', 'benchmark', 8.0)
        if benchmark is None:
            benchmark = 8.0

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=satisfaction_scores, nbinsx=10,
                                   marker_color='mediumseagreen', name='Satisfaction Scores'))
        fig.add_vline(x=benchmark, line_dash="dash", line_color="red",
                      annotation_text=f"Benchmark: {benchmark}",
                      annotation_position="top right")
        fig.update_layout(
            title='Patient Satisfaction Score Distribution',
            xaxis_title='Satisfaction Score (1-10)',
            yaxis_title='Number of Patients',
            template='plotly_white', height=400,
        )
        return fig

    def create_all_visualizations(self):
        print("\n🎨 Visualization Agent: Creating charts...\n")
        charts = {
            'kpi_summary':            self.create_kpi_summary_chart(),
            'department_performance': self.create_department_performance_chart(),
            'financial_overview':     self.create_financial_overview_chart(),
            'patient_satisfaction':   self.create_patient_satisfaction_chart(),
        }
        print("\n✅ All visualizations created!\n")
        return charts


# Test the agent
if __name__ == "__main__":
    from data_loader import DataLoaderAgent
    from metrics_calculator import MetricsCalculatorAgent

    print("="*60)
    print("TESTING VISUALIZATION AGENT")
    print("="*60 + "\n")

    loader = DataLoaderAgent()
    data = loader.load_all_data()
    calculator = MetricsCalculatorAgent(data)
    metrics = calculator.calculate_all_metrics()

    visualizer = VisualizationAgent(metrics, data)
    charts = visualizer.create_all_visualizations()

    print("\n📊 Opening KPI Summary Chart in browser...")
    charts['kpi_summary'].show()

    print("\n" + "="*60)
    print("✅ VISUALIZATION AGENT TEST COMPLETE!")
    print("="*60)
