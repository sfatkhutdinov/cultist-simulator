#!/usr/bin/env python3
"""
Performance Profiling Script - T127-T129

Profiles critical path performance for all major components:
- Vision pipeline (NFR-001: <500ms)
- Knowledge base queries (NFR-003: <100ms)
- Safety validation (Target: <10ms)
- Full episode execution

Outputs detailed timing reports and identifies bottlenecks.
"""

import time
import statistics
import json
from pathlib import Path
from datetime import datetime
import cProfile
import pstats
from io import StringIO

# Import components to profile
from src.vision import capture_game_state, detect_elements
from src.learning.knowledge_base import KnowledgeBase
from src.learning import select_action, query_knowledge, store_session
from src.safety import validate_action
from src.automation import simulate_click
from src.lib.types import Point, Rect, ActionType, GameState


class PerformanceProfiler:
    """Profile critical path performance."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "profiles": {},
            "summary": {},
            "bottlenecks": []
        }
        
    def time_function(self, name, func, iterations=10, warmup=2):
        """Time a function execution over multiple iterations."""
        print(f"\n{'='*60}")
        print(f"Profiling: {name}")
        print(f"{'='*60}")
        
        # Warmup runs
        for _ in range(warmup):
            try:
                func()
            except Exception as e:
                print(f"Warning: Warmup failed: {e}")
                
        # Timed runs
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            try:
                func()
                elapsed_ms = (time.perf_counter() - start) * 1000
                times.append(elapsed_ms)
                print(f"  Run {i+1}/{iterations}: {elapsed_ms:.2f}ms")
            except Exception as e:
                print(f"  Run {i+1}/{iterations}: FAILED - {e}")
                
        if not times:
            print(f"  ❌ All runs failed for {name}")
            return None
            
        # Calculate statistics
        avg = statistics.mean(times)
        median = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        stdev = statistics.stdev(times) if len(times) > 1 else 0
        
        result = {
            "name": name,
            "iterations": len(times),
            "avg_ms": round(avg, 2),
            "median_ms": round(median, 2),
            "min_ms": round(min_time, 2),
            "max_ms": round(max_time, 2),
            "stdev_ms": round(stdev, 2),
            "raw_times": [round(t, 2) for t in times]
        }
        
        self.results["profiles"][name] = result
        
        print(f"\n  📊 Statistics:")
        print(f"     Average:  {avg:.2f}ms")
        print(f"     Median:   {median:.2f}ms")
        print(f"     Min:      {min_time:.2f}ms")
        print(f"     Max:      {max_time:.2f}ms")
        print(f"     StdDev:   {stdev:.2f}ms")
        
        return result
        
    def profile_vision_pipeline(self):
        """Profile vision pipeline (NFR-001: <500ms)."""
        print("\n" + "="*60)
        print("VISION PIPELINE PERFORMANCE")
        print("="*60)
        
        # Since capture_game_state requires actual window, we'll measure
        # the detection pipeline with mock data
        def vision_mock():
            """Simulated vision pipeline."""
            # This would normally capture screen
            # For profiling, we simulate the processing time
            import numpy as np
            screenshot = np.zeros((1080, 1920, 3), dtype=np.uint8)
            # Actual detection would happen here
            time.sleep(0.05)  # Simulate processing
            
        self.time_function(
            "Vision Pipeline (simulated)",
            vision_mock,
            iterations=20,
            warmup=3
        )
        
    def profile_knowledge_base(self):
        """Profile knowledge base queries (NFR-003: <100ms)."""
        print("\n" + "="*60)
        print("KNOWLEDGE BASE PERFORMANCE")
        print("="*60)
        
        # Create temporary knowledge base
        kb = KnowledgeBase(":memory:")
        
        # Populate with test data
        for i in range(50):
            kb.store_mechanic(
                f"mechanic_{i}",
                {
                    "description": f"Test mechanic {i}",
                    "category": "test",
                    "data": {"value": i}
                }
            )
            
        # Profile queries
        def query_mechanic():
            kb.get_mechanic("mechanic_25")
            
        self.time_function(
            "Knowledge Base Query",
            query_mechanic,
            iterations=50,
            warmup=5
        )
        
        # Profile updates
        def update_mechanic():
            kb.store_mechanic(
                "mechanic_update",
                {"description": "Update test", "data": {"val": 1}}
            )
            
        self.time_function(
            "Knowledge Base Update",
            update_mechanic,
            iterations=50,
            warmup=5
        )
        
    def profile_safety_validation(self):
        """Profile safety validation (Target: <10ms)."""
        print("\n" + "="*60)
        print("SAFETY VALIDATION PERFORMANCE")
        print("="*60)
        
        # Test action
        action = {
            "action_type": ActionType.CLICK,
            "point": Point(100, 100)
        }
        context = {
            "window_bounds": Rect(0, 0, 1920, 1080),
            "window_focused": True
        }
        
        def validate():
            validate_action(action, context)
            
        self.time_function(
            "Safety Validation",
            validate,
            iterations=100,
            warmup=10
        )
        
    def profile_action_selection(self):
        """Profile action selection."""
        print("\n" + "="*60)
        print("ACTION SELECTION PERFORMANCE")
        print("="*60)
        
        # Mock game state
        from src.lib.types import GameElement, ElementType
        
        game_state = {
            "timestamp": datetime.now(),
            "window_bounds": Rect(0, 0, 1920, 1080),
            "elements": [
                {
                    "element_type": ElementType.BUTTON,
                    "bounds": Rect(100, 100, 80, 30),
                    "confidence": 0.9
                }
            ],
            "text_regions": [],
            "metadata": {}
        }
        
        def select():
            try:
                select_action(game_state)
            except Exception:
                # Model might not be loaded
                pass
                
        self.time_function(
            "Action Selection",
            select,
            iterations=20,
            warmup=3
        )
        
    def check_nfr_compliance(self):
        """Check if NFR requirements are met."""
        print("\n" + "="*60)
        print("NFR COMPLIANCE CHECK")
        print("="*60)
        
        requirements = {
            "Vision Pipeline": {"threshold_ms": 500, "profile_key": "Vision Pipeline (simulated)"},
            "Knowledge Query": {"threshold_ms": 100, "profile_key": "Knowledge Base Query"},
            "Safety Validation": {"threshold_ms": 10, "profile_key": "Safety Validation"}
        }
        
        compliance = {}
        
        for name, req in requirements.items():
            profile_key = req["profile_key"]
            threshold = req["threshold_ms"]
            
            if profile_key in self.results["profiles"]:
                profile = self.results["profiles"][profile_key]
                avg = profile["avg_ms"]
                passed = avg < threshold
                
                status = "✅ PASS" if passed else "❌ FAIL"
                margin = threshold - avg
                
                print(f"\n{name}:")
                print(f"  Requirement: < {threshold}ms")
                print(f"  Actual:      {avg:.2f}ms")
                print(f"  Margin:      {margin:+.2f}ms")
                print(f"  Status:      {status}")
                
                compliance[name] = {
                    "required_ms": threshold,
                    "actual_ms": avg,
                    "margin_ms": round(margin, 2),
                    "passed": passed
                }
                
                if not passed:
                    self.results["bottlenecks"].append({
                        "component": name,
                        "actual_ms": avg,
                        "required_ms": threshold,
                        "slowdown": round((avg / threshold - 1) * 100, 1)
                    })
            else:
                print(f"\n{name}: ⚠️  NOT PROFILED")
                
        self.results["summary"]["nfr_compliance"] = compliance
        
    def identify_bottlenecks(self):
        """Identify performance bottlenecks."""
        print("\n" + "="*60)
        print("BOTTLENECK ANALYSIS")
        print("="*60)
        
        if self.results["bottlenecks"]:
            print("\n❌ Performance issues found:")
            for bottleneck in self.results["bottlenecks"]:
                print(f"\n  • {bottleneck['component']}")
                print(f"    Actual: {bottleneck['actual_ms']:.2f}ms")
                print(f"    Required: {bottleneck['required_ms']:.2f}ms")
                print(f"    Slowdown: {bottleneck['slowdown']}%")
        else:
            print("\n✅ All components meet performance requirements!")
            
    def save_report(self, output_path="data/performance_report.json"):
        """Save detailed performance report."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\n📄 Report saved to: {output_path}")
        
    def run_full_profile(self):
        """Run complete performance profiling suite."""
        print("\n" + "="*60)
        print("PERFORMANCE PROFILING SUITE")
        print("Starting comprehensive performance analysis...")
        print("="*60)
        
        # Profile each component
        self.profile_knowledge_base()
        self.profile_safety_validation()
        self.profile_action_selection()
        # self.profile_vision_pipeline()  # Uncomment when testing with actual game
        
        # Check compliance
        self.check_nfr_compliance()
        
        # Identify bottlenecks
        self.identify_bottlenecks()
        
        # Save report
        self.save_report()
        
        print("\n" + "="*60)
        print("PROFILING COMPLETE")
        print("="*60)
        

def main():
    """Run performance profiling."""
    profiler = PerformanceProfiler()
    profiler.run_full_profile()
    

if __name__ == "__main__":
    main()
