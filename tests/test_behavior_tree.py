import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from behavior_tree import (
    NodeStatus,
    Blackboard,
    Action,
    Condition,
    Sequence,
    Selector,
    Parallel,
    ParallelPolicy,
    Inverter,
    Repeater,
    UntilFail,
)


class TestNodeStatus(unittest.TestCase):
    def test_enum_values(self):
        self.assertEqual(NodeStatus.SUCCESS.value, "success")
        self.assertEqual(NodeStatus.FAILURE.value, "failure")
        self.assertEqual(NodeStatus.RUNNING.value, "running")


class TestBlackboard(unittest.TestCase):
    def test_set_and_get(self):
        bb = Blackboard()
        bb.set("key", "value")
        self.assertEqual(bb.get("key"), "value")

    def test_bracket_notation(self):
        bb = Blackboard()
        bb["key"] = "value"
        self.assertEqual(bb["key"], "value")

    def test_has(self):
        bb = Blackboard()
        bb.set("key", "value")
        self.assertTrue(bb.has("key"))
        self.assertFalse(bb.has("nonexistent"))

    def test_in_operator(self):
        bb = Blackboard()
        bb.set("key", "value")
        self.assertTrue("key" in bb)
        self.assertFalse("nonexistent" in bb)

    def test_delete(self):
        bb = Blackboard()
        bb.set("key", "value")
        self.assertTrue(bb.delete("key"))
        self.assertFalse(bb.has("key"))
        self.assertFalse(bb.delete("nonexistent"))

    def test_clear(self):
        bb = Blackboard()
        bb.set("key1", "value1")
        bb.set("key2", "value2")
        bb.clear()
        self.assertFalse(bb.has("key1"))
        self.assertFalse(bb.has("key2"))

    def test_parent_inheritance(self):
        parent = Blackboard()
        parent.set("parent_key", "parent_value")
        child = Blackboard(parent)
        child.set("child_key", "child_value")
        
        self.assertEqual(child.get("parent_key"), "parent_value")
        self.assertEqual(child.get("child_key"), "child_value")
        self.assertFalse(parent.has("child_key"))


class TestAction(unittest.TestCase):
    def test_success(self):
        action = Action(lambda: NodeStatus.SUCCESS)
        self.assertEqual(action.tick(), NodeStatus.SUCCESS)

    def test_failure(self):
        action = Action(lambda: NodeStatus.FAILURE)
        self.assertEqual(action.tick(), NodeStatus.FAILURE)

    def test_running(self):
        action = Action(lambda: NodeStatus.RUNNING)
        self.assertEqual(action.tick(), NodeStatus.RUNNING)


class TestCondition(unittest.TestCase):
    def test_true(self):
        cond = Condition(lambda: True)
        self.assertEqual(cond.tick(), NodeStatus.SUCCESS)

    def test_false(self):
        cond = Condition(lambda: False)
        self.assertEqual(cond.tick(), NodeStatus.FAILURE)


class TestSequence(unittest.TestCase):
    def test_all_success(self):
        seq = Sequence([
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.SUCCESS),
        ])
        self.assertEqual(seq.tick(), NodeStatus.SUCCESS)

    def test_one_failure(self):
        seq = Sequence([
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.FAILURE),
            Action(lambda: NodeStatus.SUCCESS),
        ])
        self.assertEqual(seq.tick(), NodeStatus.FAILURE)

    def test_running(self):
        seq = Sequence([
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.RUNNING),
            Action(lambda: NodeStatus.SUCCESS),
        ])
        self.assertEqual(seq.tick(), NodeStatus.RUNNING)


class TestSelector(unittest.TestCase):
    def test_one_success(self):
        sel = Selector([
            Action(lambda: NodeStatus.FAILURE),
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.FAILURE),
        ])
        self.assertEqual(sel.tick(), NodeStatus.SUCCESS)

    def test_all_failure(self):
        sel = Selector([
            Action(lambda: NodeStatus.FAILURE),
            Action(lambda: NodeStatus.FAILURE),
        ])
        self.assertEqual(sel.tick(), NodeStatus.FAILURE)

    def test_running(self):
        sel = Selector([
            Action(lambda: NodeStatus.FAILURE),
            Action(lambda: NodeStatus.RUNNING),
        ])
        self.assertEqual(sel.tick(), NodeStatus.RUNNING)


class TestParallel(unittest.TestCase):
    def test_require_all_success(self):
        par = Parallel([
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.SUCCESS),
        ], policy=ParallelPolicy.REQUIRE_ALL)
        self.assertEqual(par.tick(), NodeStatus.SUCCESS)

    def test_require_all_failure(self):
        par = Parallel([
            Action(lambda: NodeStatus.SUCCESS),
            Action(lambda: NodeStatus.FAILURE),
        ], policy=ParallelPolicy.REQUIRE_ALL)
        self.assertEqual(par.tick(), NodeStatus.FAILURE)

    def test_require_one_success(self):
        par = Parallel([
            Action(lambda: NodeStatus.FAILURE),
            Action(lambda: NodeStatus.SUCCESS),
        ], policy=ParallelPolicy.REQUIRE_ONE)
        self.assertEqual(par.tick(), NodeStatus.SUCCESS)

    def test_require_one_all_failure(self):
        par = Parallel([
            Action(lambda: NodeStatus.FAILURE),
            Action(lambda: NodeStatus.FAILURE),
        ], policy=ParallelPolicy.REQUIRE_ONE)
        self.assertEqual(par.tick(), NodeStatus.FAILURE)


class TestInverter(unittest.TestCase):
    def test_invert_success(self):
        inv = Inverter(Action(lambda: NodeStatus.SUCCESS))
        self.assertEqual(inv.tick(), NodeStatus.FAILURE)

    def test_invert_failure(self):
        inv = Inverter(Action(lambda: NodeStatus.FAILURE))
        self.assertEqual(inv.tick(), NodeStatus.SUCCESS)

    def test_invert_running(self):
        inv = Inverter(Action(lambda: NodeStatus.RUNNING))
        self.assertEqual(inv.tick(), NodeStatus.RUNNING)


class TestRepeater(unittest.TestCase):
    def test_repeat_n_times(self):
        count = 0
        def callback():
            nonlocal count
            count += 1
            return NodeStatus.SUCCESS
        
        rep = Repeater(Action(callback), times=3)
        self.assertEqual(rep.tick(), NodeStatus.SUCCESS)
        self.assertEqual(count, 3)

    def test_repeat_with_failure(self):
        count = 0
        def callback():
            nonlocal count
            count += 1
            if count == 2:
                return NodeStatus.FAILURE
            return NodeStatus.SUCCESS
        
        rep = Repeater(Action(callback), times=5)
        self.assertEqual(rep.tick(), NodeStatus.FAILURE)
        self.assertEqual(count, 2)


class TestUntilFail(unittest.TestCase):
    def test_until_fail(self):
        count = 0
        def callback():
            nonlocal count
            count += 1
            if count == 3:
                return NodeStatus.FAILURE
            return NodeStatus.SUCCESS
        
        uf = UntilFail(Action(callback))
        self.assertEqual(uf.tick(), NodeStatus.SUCCESS)
        self.assertEqual(count, 3)


class TestBlackboardIntegration(unittest.TestCase):
    def test_node_blackboard_sharing(self):
        bb = Blackboard()
        
        def set_value():
            bb.set("test_key", "test_value")
            return NodeStatus.SUCCESS
        
        def check_value():
            return bb.get("test_key") == "test_value"
        
        seq = Sequence([
            Action(set_value),
            Condition(check_value),
        ])
        seq.blackboard = bb
        
        self.assertEqual(seq.tick(), NodeStatus.SUCCESS)


if __name__ == "__main__":
    unittest.main()
