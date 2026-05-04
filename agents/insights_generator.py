"""
Insights Generator Agent
Uses GPT-4 to analyze metrics and generate actionable recommendations
"""

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class InsightsGeneratorAgent:
    """
    AI-powered agent that generates insights from clinical metrics
    """

    def __init__(self, metrics, data, model="gpt-4"):
        self.metrics = metrics
        self.data = data
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.3,
            openai_api_key=api_key
        )

    def _get_metric(self, key, subkey, default="N/A"):
        return self.metrics.get(key, {}).get(subkey, default)

    def _invoke_llm(self, prompt):
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            return f"Error generating response: {e}"

    def generate_executive_summary(self):
        print("📝 Generating executive summary...")

        metrics_summary = f"""
Clinical Quality:
- 30-Day Readmission: {self._get_metric('readmission_rate', 'value')}% (benchmark: {self._get_metric('readmission_rate', 'benchmark')}%)
- HAI Rate: {self._get_metric('infection_rate', 'value')}/1000 (benchmark: {self._get_metric('infection_rate', 'benchmark')}/1000)
- Mortality: {self._get_metric('mortality_rate', 'value')}% (benchmark: {self._get_metric('mortality_rate', 'benchmark')}%)
- ALOS: {self._get_metric('alos', 'value')} days (benchmark: {self._get_metric('alos', 'benchmark')} days)

Operational:
- Bed Turnover: {self._get_metric('bed_turnover', 'value')} (benchmark: {self._get_metric('bed_turnover', 'benchmark')})
- Wait Time: {self._get_metric('wait_time', 'value')} min (benchmark: {self._get_metric('wait_time', 'benchmark')} min)
- No-Show Rate: {self._get_metric('no_show_rate', 'value')}% (benchmark: {self._get_metric('no_show_rate', 'benchmark')}%)
- ER Wait Time: {self._get_metric('er_wait_time', 'value')} min (benchmark: {self._get_metric('er_wait_time', 'benchmark')} min)

Financial:
- Claim Denial: {self._get_metric('denial_rate', 'value')}% (benchmark: {self._get_metric('denial_rate', 'benchmark')}%)
- Days in A/R: {self._get_metric('days_in_ar', 'value')} days (benchmark: {self._get_metric('days_in_ar', 'benchmark')} days)
- Collection Rate: {self._get_metric('collection_rate', 'value')}% (benchmark: {self._get_metric('collection_rate', 'benchmark')}%)
- Cost per Visit: {self._get_metric('cost_per_visit', 'value')} (benchmark: {self._get_metric('cost_per_visit', 'benchmark')})

Patient Experience:
- Satisfaction: {self._get_metric('satisfaction', 'value')}/10 (benchmark: {self._get_metric('satisfaction', 'benchmark')}/10)
"""

        prompt = f"""You are a healthcare analytics consultant analyzing hospital performance data.

Hospital Metrics:
{metrics_summary}

Generate a concise executive summary (3-4 paragraphs) that:
1. Highlights the hospital's top 3 strengths
2. Identifies the 3 most critical issues requiring immediate attention
3. Estimates the potential financial impact of addressing these issues
4. Provides 2-3 strategic recommendations

Be specific, data-driven, and actionable. Use professional healthcare terminology.
"""

        return self._invoke_llm(prompt)

    def analyze_specific_metric(self, metric_name, user_question=None):
        print(f"🔍 Analyzing {metric_name}...")

        metric_data = self.metrics.get(metric_name)
        if not metric_data:
            return f"Metric '{metric_name}' not found."

        context = ""
        if metric_name == 'readmission_rate':
            readmit_count = len(self.data.get('readmissions', []))
            context = f"Total readmissions: {readmit_count}. "
        elif metric_name == 'infection_rate':
            infections = self.data.get('infections')
            if infections is not None:
                infection_types = infections['infection_type'].value_counts()
                context = f"Infection breakdown: {infection_types.to_dict()}. "
        elif metric_name == 'denial_rate':
            claims = self.data.get('claims')
            if claims is not None:
                denial_reasons = claims[claims['claim_status'] == 'denied']['denial_reason'].value_counts()
                context = f"Top denial reasons: {denial_reasons.head(3).to_dict()}. "

        question = user_question or f"Why is our {metric_name} at this level and how can we improve it?"

        prompt = f"""You are a healthcare data analyst. Analyze this specific metric:

Metric: {metric_name}
Current Value: {metric_data}
Additional Context: {context}

User Question: {question}

Provide a detailed analysis including:
1. What this metric tells us about hospital performance
2. Root cause analysis (what's driving the numbers)
3. Comparison to benchmark and what the gap means
4. Specific, actionable recommendations to improve
5. Expected timeline and effort for improvement

Be specific and practical.
"""

        return self._invoke_llm(prompt)

    def answer_custom_question(self, question):
        print(f"💬 Answering: {question}")

        patients      = self.data.get('patients')
        readmissions  = self.data.get('readmissions')
        infections    = self.data.get('infections')
        claims        = self.data.get('claims')
        departments   = patients['department'].unique().tolist() if patients is not None else []

        full_context = f"""
Hospital Data Summary:
- Total Patients: {len(patients) if patients is not None else 0}
- Total Readmissions: {len(readmissions) if readmissions is not None else 0}
- Total Infections: {len(infections) if infections is not None else 0}
- Total Claims: {len(claims) if claims is not None else 0}
- Departments: {departments}

Key Metrics:
{self._format_all_metrics()}
"""

        prompt = f"""You are an AI clinical data analyst. You have access to hospital performance data.

Available Data:
{full_context}

User Question: {question}

Provide a detailed, data-driven answer. If you need to make calculations or comparisons, do so based on the data provided. Be specific and cite numbers when possible.

If the question cannot be fully answered with the available data, explain what data would be needed.
"""

        return self._invoke_llm(prompt)

    def generate_action_plan(self, focus_area):
        print(f"📋 Generating action plan for: {focus_area}")

        relevant_metrics = self._get_relevant_metrics(focus_area)

        prompt = f"""You are a healthcare quality improvement consultant.

Focus Area: {focus_area}
Current Metrics: {relevant_metrics}

Create a detailed 90-day action plan to improve performance in this area. Include:

1. IMMEDIATE ACTIONS (Week 1-2):
   - Specific tasks
   - Responsible parties
   - Quick wins

2. SHORT-TERM INITIATIVES (Week 3-8):
   - Process improvements
   - Training programs
   - System changes

3. LONG-TERM STRATEGIES (Week 9-12):
   - Sustainability measures
   - Continuous monitoring
   - Culture changes

4. KEY PERFORMANCE INDICATORS:
   - Metrics to track
   - Target improvements
   - Review frequency

5. ESTIMATED IMPACT:
   - Expected metric improvements
   - Financial impact
   - Timeline to results

Format as a clear, actionable plan that could be presented to hospital leadership.
"""

        return self._invoke_llm(prompt)

    def _format_all_metrics(self):
        output = []
        for key, value in self.metrics.items():
            if isinstance(value, dict) and 'value' in value:
                benchmark = value.get('benchmark', 'N/A')
                output.append(f"- {key}: {value['value']} (benchmark: {benchmark})")
        return "\n".join(output)

    def _get_relevant_metrics(self, focus_area):
        area_mapping = {
            'clinical quality': ['readmission_rate', 'infection_rate', 'mortality_rate', 'alos'],
            'operations': ['bed_turnover', 'wait_time', 'no_show_rate', 'er_wait_time'],
            'financial': ['denial_rate', 'days_in_ar', 'cost_per_visit', 'collection_rate'],
            'patient experience': ['satisfaction', 'wait_time', 'no_show_rate'],
        }

        focus_lower = focus_area.lower()
        relevant_keys = []

        for area, keys in area_mapping.items():
            if area in focus_lower or focus_lower in area:
                relevant_keys = keys
                break

        if not relevant_keys:
            relevant_keys = list(self.metrics.keys())[:5]

        return "\n".join([
            f"- {key}: {self.metrics[key].get('value', 'N/A')} (benchmark: {self.metrics[key].get('benchmark', 'N/A')})"
            for key in relevant_keys if key in self.metrics
        ])


# Test the agent
if __name__ == "__main__":
    from data_loader import DataLoaderAgent
    from metrics_calculator import MetricsCalculatorAgent

    print("="*60)
    print("TESTING INSIGHTS GENERATOR AGENT")
    print("="*60 + "\n")

    loader = DataLoaderAgent()
    data = loader.load_all_data()

    calculator = MetricsCalculatorAgent(data)
    metrics = calculator.calculate_all_metrics()

    insights = InsightsGeneratorAgent(metrics, data)

    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60 + "\n")

    summary = insights.generate_executive_summary()
    print(summary)

    print("\n" + "="*60)
    print("✅ INSIGHTS GENERATOR AGENT TEST COMPLETE!")
    print("="*60)
