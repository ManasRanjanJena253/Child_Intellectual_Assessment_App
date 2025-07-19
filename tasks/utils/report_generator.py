import os
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pypdf import PdfReader
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()


@dataclass
class ChildInfo:
    name: str
    age: str
    sex: str
    age_group: str


@dataclass
class AssessmentResults:
    overall_score: float
    total_completed: int
    total_tasks: int
    physical_status: str
    linguistic_status: str
    cognitive_results: List[Dict]
    detailed_results: Dict


class AIReportGenerator:
    def __init__(self):
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]

        if not api_key:
            raise ValueError("Please set GEMINI_API_KEY in your environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def extract_pdf_content(self, pdf_path: str) -> Dict[str, Any]:
        try:
            reader = PdfReader(pdf_path)
            text_content = "\n".join(page.extract_text() for page in reader.pages)
            extracted_data = self._parse_pdf_text(text_content)
            return {
                "success": True,
                "content": text_content,
                "parsed_data": extracted_data,
                "total_pages": len(reader.pages),
                "extraction_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract PDF content: {str(e)}",
                "content": "",
                "parsed_data": {}
            }

    def _parse_pdf_text(self, text_content: str) -> Dict[str, Any]:
        lines = text_content.split('\n')
        parsed_data = {
            "child_info": {},
            "parent_info": {},
            "assessment_results": {},
            "detailed_results": {},
            "recommendations": [],
            "physical_tasks": [],
            "linguistic_tasks": [],
            "cognitive_tasks": []
        }

        try:
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Section identification with enhanced parsing
                if "Child Information:" in line or "Child Info:" in line:
                    current_section = "child_info"
                    continue
                elif "Parent/Guardian Information:" in line or "Parent Info:" in line:
                    current_section = "parent_info"
                    continue
                elif "Assessment Results" in line or "Overall Results" in line:
                    current_section = "assessment_results"
                    continue
                elif "Physical Tasks" in line or "Physical Development" in line:
                    current_section = "physical_tasks"
                    continue
                elif "Linguistic Tasks" in line or "Language Development" in line:
                    current_section = "linguistic_tasks"
                    continue
                elif "Cognitive Skills" in line or "Cognitive Development" in line:
                    current_section = "cognitive_tasks"
                    continue
                elif "Detailed Results:" in line:
                    current_section = "detailed_results"
                    continue
                elif "Recommendations:" in line:
                    current_section = "recommendations"
                    continue

                # Enhanced data extraction
                if ":" in line and current_section and current_section not in ["recommendations", "physical_tasks",
                                                                               "linguistic_tasks", "cognitive_tasks"]:
                    key, value = line.split(":", 1)
                    parsed_data[current_section][key.strip().lower().replace(" ", "_")] = value.strip()
                elif current_section == "recommendations":
                    if line and not line.startswith("-"):
                        parsed_data["recommendations"].append(line)
                elif current_section in ["physical_tasks", "linguistic_tasks", "cognitive_tasks"]:
                    if "completed" in line.lower() or "passed" in line.lower():
                        parsed_data[current_section].append({"task": line, "status": "completed"})
                    elif "not completed" in line.lower() or "failed" in line.lower():
                        parsed_data[current_section].append({"task": line, "status": "not_completed"})

            # Enhanced score processing
            if "overall_score" in parsed_data["assessment_results"]:
                try:
                    score_text = parsed_data["assessment_results"]["overall_score"]
                    score_match = re.search(r'(\d+\.?\d*)%?', score_text)
                    if score_match:
                        parsed_data["assessment_results"]["score_percentage"] = float(score_match.group(1))
                    else:
                        parsed_data["assessment_results"]["score_percentage"] = 0
                except:
                    parsed_data["assessment_results"]["score_percentage"] = 0

        except Exception as e:
            parsed_data["parsing_error"] = str(e)

        return parsed_data

    def analyze_development_patterns(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Enhanced prompt for comprehensive analysis
            prompt = f"""
You are a world-renowned child developmental psychologist and pediatric assessment specialist with over 20 years of experience. 
Analyze the following comprehensive assessment data and generate an exceptionally detailed, insightful developmental report.

CRITICAL INSTRUCTIONS:
1. Provide deep, nuanced analysis that goes beyond surface-level observations
2. Include developmental milestones context for the child's age
3. Identify patterns, correlations, and potential underlying factors
4. Offer evidence-based insights and professional recommendations
5. Use a warm, professional tone that's accessible to parents
6. Structure the response with clear markdown sections as specified below

REQUIRED REPORT STRUCTURE:

# Executive Summary
[Provide a comprehensive 4-6 sentence overview of the child's overall developmental status, highlighting key findings, overall trajectory, and primary areas of focus. This should give parents a complete picture at a glance.]

# Child Information Summary
**Name:** [Child's name]
**Age:** [Age with developmental stage context]
**Gender:** [Gender]
**Assessment Date:** [Date]
**Overall Development Level:** [Advanced/On Track/Needs Support with detailed explanation]

# Developmental Domain Analysis

## Physical Development
[Provide detailed analysis of gross motor, fine motor, and physical coordination skills. Include:]
- Current performance level vs. age-appropriate milestones
- Specific strengths observed
- Areas requiring attention
- Developmental trajectory implications
- Connection to overall health and wellbeing

## Linguistic Development  
[Comprehensive analysis of language and communication skills including:]
- Receptive language abilities (understanding)
- Expressive language skills (speaking/communication)
- Vocabulary development and complexity
- Social communication patterns
- Literacy readiness or reading skills (age-appropriate)
- Comparison to typical developmental patterns

## Cognitive Development
[In-depth analysis of thinking, learning, and problem-solving abilities:]
- Executive function skills (attention, working memory, flexibility)
- Problem-solving approaches and strategies
- Abstract thinking development
- Learning style preferences
- Memory and retention patterns
- Academic readiness or performance indicators

# Strengths and Exceptional Abilities
[Detailed exploration of the child's strongest areas, including:]
- Specific skills that stand out
- Natural talents and inclinations
- Learning preferences and optimal conditions
- Ways to leverage these strengths for overall development

# Areas for Growth and Development
[Thoughtful analysis of areas needing attention, presented constructively:]
- Specific skills requiring development
- Potential underlying factors
- Developmental opportunities
- Realistic expectations and timeline

# Environmental and Contextual Factors
[Analysis of how external factors may influence development:]
- Home environment considerations
- Social and emotional context
- Educational setting impact
- Cultural and familial factors

# Detailed Professional Recommendations

## Immediate Actions (Next 1-3 months)
[Specific, actionable recommendations with clear timelines]

## Medium-term Goals (3-6 months)
[Strategic developmental targets with measurement criteria]

## Long-term Development Plan (6-12 months)
[Comprehensive growth trajectory with milestone markers]

## Parent and Caregiver Strategies
[Practical, daily implementation strategies for families]

## Professional Support Recommendations
[When and what type of additional support might be beneficial]

# Progress Monitoring and Follow-up
[Guidelines for tracking development and when to reassess]

# Resources and Support
[Specific resources, activities, and support options for continued development]

---

ASSESSMENT CONTENT TO ANALYZE:
{extracted_data['content']}

PARSED DATA CONTEXT:
Child Info: {extracted_data['parsed_data'].get('child_info', {})}
Assessment Results: {extracted_data['parsed_data'].get('assessment_results', {})}
Physical Tasks: {len(extracted_data['parsed_data'].get('physical_tasks', []))} tasks
Linguistic Tasks: {len(extracted_data['parsed_data'].get('linguistic_tasks', []))} tasks  
Cognitive Tasks: {len(extracted_data['parsed_data'].get('cognitive_tasks', []))} tasks

Please provide a thorough, insightful analysis that will genuinely help parents understand their child's development and provide actionable guidance for supporting their growth.
"""

            response = self.model.generate_content(prompt)

            # Enhanced metadata extraction
            metadata = self._extract_analysis_metadata(response.text, extracted_data)

            return {
                "success": True,
                "raw_response": response.text,
                "structured_analysis": self._parse_ai_response(response.text),
                "metadata": metadata
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": self._enhanced_fallback_analysis(extracted_data)
            }

    def _extract_analysis_metadata(self, ai_response: str, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured metadata from AI response for better integration."""
        parsed_data = extracted_data["parsed_data"]

        # Extract development level from AI response
        dev_level_match = re.search(r'Overall Development Level:\*\*\s*([^*\n]+)', ai_response)
        development_level = dev_level_match.group(1).strip() if dev_level_match else "Assessment Pending"

        # Calculate domain scores from parsed data
        domain_scores = self._calculate_domain_scores(parsed_data)

        # Extract key insights
        strengths = self._extract_section_content(ai_response, "Strengths and Exceptional Abilities")
        growth_areas = self._extract_section_content(ai_response, "Areas for Growth and Development")
        recommendations = self._extract_section_content(ai_response, "Detailed Professional Recommendations")

        return {
            "development_level": development_level,
            "domain_scores": domain_scores,
            "key_strengths": strengths[:200] + "..." if len(strengths) > 200 else strengths,
            "growth_areas": growth_areas[:200] + "..." if len(growth_areas) > 200 else growth_areas,
            "top_recommendations": recommendations[:300] + "..." if len(recommendations) > 300 else recommendations,
            "assessment_completeness": self._assess_completeness(parsed_data),
            "risk_factors": self._identify_risk_factors(parsed_data, ai_response),
            "exceptional_abilities": self._identify_exceptional_abilities(ai_response)
        }

    def _calculate_domain_scores(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed domain scores from parsed assessment data."""
        scores = {}

        # Physical domain
        physical_tasks = parsed_data.get("physical_tasks", [])
        if physical_tasks:
            completed = sum(1 for task in physical_tasks if task.get("status") == "completed")
            physical_score = (completed / len(physical_tasks)) * 100
        else:
            physical_score = 0

        scores["physical"] = {
            "score": physical_score,
            "tasks_completed": len([t for t in physical_tasks if t.get("status") == "completed"]),
            "total_tasks": len(physical_tasks),
            "percentile": self._score_to_percentile(physical_score),
            "status": self._score_to_status(physical_score)
        }

        # Linguistic domain
        linguistic_tasks = parsed_data.get("linguistic_tasks", [])
        if linguistic_tasks:
            completed = sum(1 for task in linguistic_tasks if task.get("status") == "completed")
            linguistic_score = (completed / len(linguistic_tasks)) * 100
        else:
            linguistic_score = 0

        scores["linguistic"] = {
            "score": linguistic_score,
            "tasks_completed": len([t for t in linguistic_tasks if t.get("status") == "completed"]),
            "total_tasks": len(linguistic_tasks),
            "percentile": self._score_to_percentile(linguistic_score),
            "status": self._score_to_status(linguistic_score)
        }

        # Cognitive domain
        cognitive_tasks = parsed_data.get("cognitive_tasks", [])
        if cognitive_tasks:
            completed = sum(1 for task in cognitive_tasks if task.get("status") == "completed")
            cognitive_score = (completed / len(cognitive_tasks)) * 100
        else:
            cognitive_score = 0

        scores["cognitive"] = {
            "score": cognitive_score,
            "tasks_completed": len([t for t in cognitive_tasks if t.get("status") == "completed"]),
            "total_tasks": len(cognitive_tasks),
            "percentile": self._score_to_percentile(cognitive_score),
            "status": self._score_to_status(cognitive_score)
        }

        return scores

    def _score_to_percentile(self, score: float) -> int:
        """Convert score to percentile ranking."""
        if score >= 95:
            return 98
        elif score >= 90:
            return 90
        elif score >= 85:
            return 80
        elif score >= 75:
            return 65
        elif score >= 65:
            return 50
        elif score >= 55:
            return 35
        elif score >= 45:
            return 20
        else:
            return 10

    def _score_to_status(self, score: float) -> str:
        """Convert score to developmental status."""
        if score >= 85:
            return "Advanced"
        elif score >= 65:
            return "On Track"
        elif score >= 45:
            return "Developing"
        else:
            return "Needs Support"

    def _extract_section_content(self, text: str, section_title: str) -> str:
        """Extract content from specific markdown section."""
        pattern = rf'#{1, 3}\s*{re.escape(section_title)}.*?\n(.*?)(?=\n#{1, 3}|\Z)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _assess_completeness(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the completeness of the assessment data."""
        total_tasks = (len(parsed_data.get("physical_tasks", [])) +
                       len(parsed_data.get("linguistic_tasks", [])) +
                       len(parsed_data.get("cognitive_tasks", [])))

        completed_tasks = sum(1 for task_list in [
            parsed_data.get("physical_tasks", []),
            parsed_data.get("linguistic_tasks", []),
            parsed_data.get("cognitive_tasks", [])
        ] for task in task_list if task.get("status") == "completed")

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "assessment_quality": "Comprehensive" if total_tasks >= 15 else "Standard" if total_tasks >= 8 else "Limited"
        }

    def _identify_risk_factors(self, parsed_data: Dict[str, Any], ai_response: str) -> List[str]:
        """Identify potential risk factors from the assessment."""
        risk_factors = []

        # Check for developmental delays
        domain_scores = self._calculate_domain_scores(parsed_data)
        for domain, scores in domain_scores.items():
            if scores["score"] < 45:
                risk_factors.append(f"Significant delays in {domain} development")
            elif scores["score"] < 65:
                risk_factors.append(f"Mild delays in {domain} development")

        # Check AI response for specific concerns
        concern_keywords = ["concern", "delay", "difficulty", "challenge", "support needed", "intervention"]
        for keyword in concern_keywords:
            if keyword.lower() in ai_response.lower():
                risk_factors.append(f"Professional attention recommended for identified {keyword}")

        return risk_factors[:5]  # Limit to top 5

    def _identify_exceptional_abilities(self, ai_response: str) -> List[str]:
        """Identify exceptional abilities from AI analysis."""
        abilities = []

        # Look for positive indicators in AI response
        strength_indicators = ["exceptional", "advanced", "outstanding", "gifted", "remarkable", "excellent"]

        for indicator in strength_indicators:
            if indicator.lower() in ai_response.lower():
                context_match = re.search(rf'.{{0,50}}{re.escape(indicator)}.{{0,50}}', ai_response, re.IGNORECASE)
                if context_match:
                    abilities.append(context_match.group().strip())

        return abilities[:3]  # Limit to top 3

    def _parse_ai_response(self, ai_response: str) -> Dict[str, str]:
        """Parse AI response into structured sections."""
        sections = {}
        current_section = None
        content_lines = []

        for line in ai_response.split('\n'):
            if line.strip().startswith('#'):
                if current_section:
                    sections[current_section] = '\n'.join(content_lines).strip()
                current_section = line.strip('#').strip()
                content_lines = []
            else:
                content_lines.append(line)

        if current_section and content_lines:
            sections[current_section] = '\n'.join(content_lines).strip()

        return sections

    def _enhanced_fallback_analysis(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback analysis when AI generation fails."""
        parsed = extracted_data["parsed_data"]
        child_info = parsed.get("child_info", {})

        # Calculate comprehensive scores
        domain_scores = self._calculate_domain_scores(parsed)
        overall_score = sum(scores["score"] for scores in domain_scores.values()) / len(
            domain_scores) if domain_scores else 0

        # Determine development level
        if overall_score >= 85:
            level = "Advanced"
            summary = "demonstrates exceptional development across multiple domains with skills often exceeding age-appropriate expectations."
        elif overall_score >= 65:
            level = "On Track"
            summary = "shows healthy, typical development with strengths in several areas and good overall progress."
        else:
            level = "Needs Support"
            summary = "would benefit from additional support and targeted interventions to reach developmental milestones."

        return {
            "development_level": level,
            "overall_score": overall_score,
            "domain_scores": domain_scores,
            "executive_summary": f"Based on comprehensive assessment, {child_info.get('name', 'this child')} {summary}",
            "key_strengths": self._generate_fallback_strengths(domain_scores),
            "growth_areas": self._generate_fallback_growth_areas(domain_scores),
            "recommendations": self._generate_fallback_recommendations(domain_scores, level),
            "assessment_completeness": self._assess_completeness(parsed)
        }

    def _generate_fallback_strengths(self, domain_scores: Dict[str, Any]) -> List[str]:
        """Generate strengths based on domain scores."""
        strengths = []
        for domain, scores in domain_scores.items():
            if scores["score"] >= 75:
                strengths.append(f"Strong {domain} development with {scores['score']:.0f}% task completion")

        if not strengths:
            strengths.append("Demonstrates engagement and effort in assessment activities")

        return strengths

    def _generate_fallback_growth_areas(self, domain_scores: Dict[str, Any]) -> List[str]:
        """Generate growth areas based on domain scores."""
        growth_areas = []
        for domain, scores in domain_scores.items():
            if scores["score"] < 65:
                growth_areas.append(f"{domain.title()} skills development (current level: {scores['score']:.0f}%)")

        if not growth_areas:
            growth_areas.append("Continued practice and reinforcement of developing skills")

        return growth_areas

    def _generate_fallback_recommendations(self, domain_scores: Dict[str, Any], level: str) -> List[str]:
        """Generate recommendations based on assessment results."""
        recommendations = []

        if level == "Advanced":
            recommendations.extend([
                "Provide enrichment activities to challenge advanced abilities",
                "Consider accelerated learning opportunities in strong domains",
                "Maintain regular developmental monitoring to track continued progress"
            ])
        elif level == "On Track":
            recommendations.extend([
                "Continue current supportive practices and routines",
                "Provide varied learning experiences to strengthen all domains",
                "Regular encouragement and positive reinforcement for efforts"
            ])
        else:
            recommendations.extend([
                "Implement targeted interventions for areas of concern",
                "Consider consultation with developmental specialists",
                "Increase structured practice time for developing skills",
                "Create supportive, low-pressure learning environment"
            ])

        # Domain-specific recommendations
        for domain, scores in domain_scores.items():
            if scores["score"] < 50:
                recommendations.append(f"Seek specialized support for {domain} development")

        return recommendations

    def generate_comprehensive_report(self, analysis_results: Dict[str, Any], extracted_data: Dict[str, Any]) -> str:
        """Generate comprehensive report with enhanced formatting and content."""
        if not analysis_results.get("success"):
            return self._generate_enhanced_fallback_report(analysis_results.get("fallback_analysis", {}),
                                                           extracted_data)

        # Add metadata and enhancement to the AI-generated report
        metadata = analysis_results.get("metadata", {})
        base_report = analysis_results["raw_response"]

        # Enhanced header with assessment metadata
        assessment_info = f"""
# 🌟 Comprehensive Child Development Assessment Report

*Generated using Advanced AI Analysis • Assessment Date: {datetime.now().strftime('%B %d, %Y')}*

---

## 📊 Assessment Overview

**Completion Rate:** {metadata.get('assessment_completeness', {}).get('completion_rate', 0):.1f}%  
**Assessment Quality:** {metadata.get('assessment_completeness', {}).get('assessment_quality', 'Standard')}  
**Total Tasks Evaluated:** {metadata.get('assessment_completeness', {}).get('total_tasks', 'N/A')}  
**Development Level:** {metadata.get('development_level', 'Assessment Pending')}

---

"""

        # Add risk factors and exceptional abilities if identified
        additional_insights = ""

        if metadata.get('risk_factors'):
            additional_insights += f"""
## ⚠️ Areas Requiring Attention

{chr(10).join(f"- {factor}" for factor in metadata['risk_factors'])}

"""

        if metadata.get('exceptional_abilities'):
            additional_insights += f"""
## ⭐ Exceptional Abilities Identified

{chr(10).join(f"- {ability}" for ability in metadata['exceptional_abilities'])}

"""

        # Footer with next steps
        footer = f"""

---

## 📋 Assessment Summary

This comprehensive analysis was generated using advanced AI technology specifically trained in child development assessment. The recommendations provided are based on current developmental research and best practices in pediatric psychology.

**Next Steps:**
1. Review all sections of this report thoroughly
2. Implement immediate action recommendations
3. Schedule follow-up assessment in 3-6 months
4. Contact recommended professionals if indicated

**Questions or Concerns?**
Please consult with your pediatrician or a licensed child development specialist for personalized guidance.

---

*Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} using Gemini AI Technology*
*Assessment data processed: {extracted_data.get('total_pages', 1)} page(s) of source material*
        """

        return assessment_info + base_report + additional_insights + footer

    def _generate_enhanced_fallback_report(self, analysis_results: Dict[str, Any],
                                           extracted_data: Dict[str, Any]) -> str:
        """Generate enhanced fallback report when AI analysis fails."""
        parsed = extracted_data["parsed_data"]
        child_info = parsed.get("child_info", {})

        return f"""
# 🌟 Child Development Assessment Report

*Generated on {datetime.now().strftime('%B %d, %Y')}*

## Child Information Summary

**Name:** {child_info.get('name', 'Not specified')}  
**Age:** {child_info.get('age', 'Not specified')}  
**Gender:** {child_info.get('sex', 'Not specified')}  
**Assessment Date:** {datetime.now().strftime('%B %d, %Y')}  
**Overall Development Level:** {analysis_results.get('development_level', 'Assessment Pending')}

## Executive Summary

{analysis_results.get('executive_summary', 'Assessment completed with comprehensive evaluation across multiple developmental domains.')}

## Developmental Domain Analysis

### Overall Performance: {analysis_results.get('overall_score', 0):.1f}%

{self._format_domain_analysis(analysis_results.get('domain_scores', {}))}

## Strengths and Exceptional Abilities

{chr(10).join(f"- {strength}" for strength in analysis_results.get('key_strengths', ['Demonstrates engagement in assessment activities']))}

## Areas for Growth and Development  

{chr(10).join(f"- {area}" for area in analysis_results.get('growth_areas', ['Continue supporting overall development']))}

## Detailed Professional Recommendations

### Immediate Actions (Next 1-3 months)
{chr(10).join(f"- {rec}" for rec in analysis_results.get('recommendations', [])[:3])}

### Medium-term Goals (3-6 months)
- Monitor progress in identified growth areas
- Implement recommended activities and interventions
- Schedule follow-up assessment

### Long-term Development Plan (6-12 months)
- Continue comprehensive developmental support
- Reassess progress and adjust strategies as needed
- Maintain focus on child's individual strengths and interests

## Progress Monitoring and Follow-up

Regular monitoring of developmental progress is recommended. Schedule follow-up assessment in 3-6 months to track improvements and adjust intervention strategies.

---

*This report was generated using standardized assessment protocols. For personalized guidance, please consult with a licensed child development specialist.*
        """.strip()

    def _format_domain_analysis(self, domain_scores: Dict[str, Any]) -> str:
        """Format domain analysis for fallback report."""
        if not domain_scores:
            return "Domain-specific analysis not available."

        analysis = ""
        for domain, scores in domain_scores.items():
            analysis += f"""
### {domain.title()} Development
- **Score:** {scores['score']:.1f}% ({scores['tasks_completed']}/{scores['total_tasks']} tasks completed)
- **Status:** {scores['status']}  
- **Percentile:** {scores['percentile']}th percentile
"""
        return analysis

    def process_pdf_to_ai_report(self, pdf_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Process PDF and generate comprehensive AI report with enhanced metadata."""
        try:
            # Extract PDF content
            extracted_data = self.extract_pdf_content(pdf_path)
            if not extracted_data["success"]:
                return False, extracted_data["error"], {}

            # Generate AI analysis
            analysis_results = self.analyze_development_patterns(extracted_data)

            # Generate comprehensive report
            report = self.generate_comprehensive_report(analysis_results, extracted_data)

            # Create comprehensive metadata
            metadata = {
                "child_name": extracted_data["parsed_data"].get("child_info", {}).get("name", "Unknown"),
                "child_age": extracted_data["parsed_data"].get("child_info", {}).get("age", "Unknown"),
                "overall_score": analysis_results.get("metadata", {}).get("assessment_completeness", {}).get(
                    "completion_rate", 0),
                "development_level": analysis_results.get("metadata", {}).get("development_level",
                                                                              "Assessment Pending"),
                "domain_scores": analysis_results.get("metadata", {}).get("domain_scores", {}),
                "gemini_success": analysis_results.get("success", False),
                "assessment_quality": analysis_results.get("metadata", {}).get("assessment_completeness", {}).get(
                    "assessment_quality", "Standard"),
                "risk_factors": analysis_results.get("metadata", {}).get("risk_factors", []),
                "exceptional_abilities": analysis_results.get("metadata", {}).get("exceptional_abilities", []),
                "timestamp": datetime.now().isoformat(),
                "report_length": len(report),
                "sections_generated": len(analysis_results.get("structured_analysis", {}))
            }

            return True, report, metadata

        except Exception as e:
            return False, f"Report generation failed: {str(e)}", {}

    def save_ai_report(self, report_content: str, child_name: str, output_dir: str = "reports") -> str:
        """Save AI report with enhanced file naming and organization."""
        os.makedirs(output_dir, exist_ok=True)

        # Create safe filename
        safe_name = "".join(c for c in child_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Comprehensive_AI_Report_{safe_name}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_content)
            return filepath
        except Exception as e:
            # Fallback to simple filename if there are issues
            simple_filename = f"AI_Report_{timestamp}.md"
            simple_filepath = os.path.join(output_dir, simple_filename)
            with open(simple_filepath, "w", encoding="utf-8") as f:
                f.write(report_content)
            return simple_filepath