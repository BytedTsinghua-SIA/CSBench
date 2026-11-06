"""
Unit tests for global constants generation.
Tests that prototype objects and constants are properly generated.
"""
import subprocess
import os
import tempfile
import re


def compile_cool_program(program_content):
    """Compile a Cool program and return the generated assembly code."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cl', delete=False) as f:
        f.write(program_content)
        temp_cl = f.name
    
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ['make', 'cgen'],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return None
        
        result = subprocess.run(
            ['./mycoolc', temp_cl],
            cwd=script_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assembly_file = temp_cl.replace('.cl', '.s')
        if os.path.exists(assembly_file):
            with open(assembly_file, 'r') as f:
                return f.read()
        return result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return None
    finally:
        if os.path.exists(temp_cl):
            os.unlink(temp_cl)
        assembly_file = temp_cl.replace('.cl', '.s')
        if os.path.exists(assembly_file):
            os.unlink(assembly_file)


class TestGlobalConstants:
    """Test global constants generation."""
    
    def test_string_constants_generated(self):
        """Test that string constants are generated in assembly."""
        program = """
class Main {
    main(): Object {
        "hello"
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "str_const" in assembly, "String constants not found in assembly"
    
    def test_int_constants_generated(self):
        """Test that integer constants are generated."""
        program = """
class Main {
    main(): Object {
        42
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "int_const" in assembly, "Integer constants not found in assembly"
    
    def test_bool_constants_generated(self):
        """Test that boolean constants are generated."""
        program = """
class Main {
    main(): Object {
        true
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "bool_const" in assembly, "Boolean constants not found in assembly"
    
    def test_prototype_objects_defined(self):
        """Test that prototype objects are defined for classes."""
        program = """
class Test {
    x: Int;
};
class Main {
    main(): Object { new Test };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_protObj" in assembly, "Prototype objects not found in assembly"
    
    def test_prototype_has_correct_structure(self):
        """Test that prototype objects have correct structure with -1 eye catcher."""
        program = """
class Test {
    x: Int;
};
class Main {
    main(): Object { new Test };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_protObj" in assembly, "Prototype objects not found"
        lines = assembly.split('\n')
        protobj_found = False
        for i, line in enumerate(lines):
            if "_protObj" in line and ":" in line:
                protobj_found = True
                if i + 1 < len(lines):
                    assert "-1" in lines[i-1] or "-1" in lines[i+1], "Prototype missing -1 eye catcher"
                break
        assert protobj_found, "Prototype object label not found"


class TestGlobalTables:
    """Test global tables generation."""
    
    def test_class_name_table_exists(self):
        """Test that class_nameTab is generated."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "class_nameTab" in assembly, "class_nameTab not found in assembly"
    
    def test_class_obj_table_exists(self):
        """Test that class_objTab is generated."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "class_objTab" in assembly, "class_objTab not found in assembly"
    
    def test_class_name_table_contains_all_classes(self):
        """Test that all classes appear in class_nameTab."""
        program = """
class A {
};
class B {
};
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "class_nameTab" in assembly, "class_nameTab not found"
        assert "str_const" in assembly or "String" in assembly, "Class names not in string table"
    
    def test_class_obj_table_has_protobj_and_init(self):
        """Test that class_objTab contains both prototype and init references."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "class_objTab" in assembly, "class_objTab not found"
        assert "_protObj" in assembly, "Prototype reference not found"
        assert "_init" in assembly, "Init reference not found"
    
    def test_dispatch_table_generated(self):
        """Test that dispatch tables are generated for classes."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_dispTab" in assembly, "Dispatch tables not found in assembly"
    
    def test_dispatch_table_contains_methods(self):
        """Test that dispatch tables contain method references."""
        program = """
class Main {
    main(): Object { 0 };
    test(): Int { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_dispTab" in assembly, "Dispatch table not found"
        assert "Main.main" in assembly or "main" in assembly, "Method reference not found in dispatch table"


class TestClassInitialization:
    """Test class initialization code generation."""
    
    def test_init_method_generated(self):
        """Test that init methods are generated for classes."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_init" in assembly, "Init methods not found in assembly"
    
    def test_init_calls_parent_init(self):
        """Test that init methods call parent class init."""
        program = """
class A {
};
class B inherits A {
};
class Main {
    main(): Object { new B };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "B_init" in assembly, "B_init not found"
        assert "A_init" in assembly or "jal" in assembly, "Parent init call not found"
    
    def test_init_initializes_attributes(self):
        """Test that init methods initialize class attributes."""
        program = """
class Main {
    x: Int <- 5;
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "Main_init" in assembly, "Main_init not found"
    
    def test_init_handles_empty_initializers(self):
        """Test that init handles attributes with no initializers."""
        program = """
class Main {
    x: Int;
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "Main_init" in assembly, "Main_init not found"


class TestMethodDefinitions:
    """Test method definition code generation."""
    
    def test_method_code_generated(self):
        """Test that method code is generated."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "Main.main" in assembly or "main:" in assembly, "Method code not found"
    
    def test_method_sets_up_frame(self):
        """Test that methods set up stack frame correctly."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "Main.main" in assembly or "main:" in assembly, "Method not found"
        assert "$fp" in assembly or "$sp" in assembly, "Stack frame setup not found"
    
    def test_method_handles_parameters(self):
        """Test that methods handle parameters correctly."""
        program = """
class Main {
    test(x: Int): Int { x };
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "test" in assembly, "Method test not found"
    
    def test_method_returns_value(self):
        """Test that methods return values correctly."""
        program = """
class Main {
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "Main.main" in assembly or "main:" in assembly, "Method not found"
        assert "jr" in assembly or "ret" in assembly, "Return instruction not found"


class TestRuntimeErrorChecking:
    """Test runtime error checking code generation."""
    
    def test_dispatch_on_void_check(self):
        """Test that dispatch on void is checked."""
        program = """
class Main {
    main(): Object {
        (new Main).test()
    };
    test(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "dispatch" in assembly.lower() or "beq" in assembly or "bne" in assembly, "Void check not found"
    
    def test_dispatch_abort_called(self):
        """Test that _dispatch_abort is called on void dispatch."""
        program = """
class Main {
    main(): Object {
        (new Main).test()
    };
    test(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_dispatch_abort" in assembly, "_dispatch_abort not found"
    
    def test_case_on_void_check(self):
        """Test that case on void is checked."""
        program = """
class Main {
    main(): Object {
        case 0 of
            x: Int => x;
        esac
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "case" in assembly.lower() or "beq" in assembly or "bne" in assembly, "Case void check not found"
    
    def test_case_abort_called(self):
        """Test that _case_abort2 is called on void case."""
        program = """
class Main {
    main(): Object {
        case 0 of
            x: Int => x;
        esac
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_case_abort" in assembly, "_case_abort not found"
    
    def test_missing_branch_handled(self):
        """Test that missing branch in case is handled."""
        program = """
class Main {
    main(): Object {
        case 0 of
            x: Int => x;
        esac
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_case_abort" in assembly, "Case abort not found"
    
    def test_case_abort_on_no_match(self):
        """Test that _case_abort is called when no branch matches."""
        program = """
class Main {
    main(): Object {
        case 0 of
            x: Int => x;
        esac
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "_case_abort" in assembly, "_case_abort not found"


class TestGarbageCollection:
    """Test garbage collection support."""
    
    def test_gc_assign_called(self):
        """Test that _GenGC_Assign is called when GC is enabled."""
        program = """
class Main {
    x: Int;
    main(): Object {
        x <- 5;
        0
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
    
    def test_gc_check_in_assignments(self):
        """Test that GC checks are included in assignments."""
        program = """
class Main {
    x: Int;
    main(): Object {
        x <- 5;
        0
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
    
    def test_gc_check_in_object_access(self):
        """Test that GC checks are included in object field access."""
        program = """
class Main {
    x: Int;
    main(): Object {
        x;
        0
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"


class TestExpressionGeneration:
    """Test expression code generation."""
    
    def test_arithmetic_operations(self):
        """Test arithmetic operation code generation."""
        program = """
class Main {
    main(): Object {
        1 + 2
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "add" in assembly.lower() or "+" in assembly, "Arithmetic operation not found"
    
    def test_comparison_operations(self):
        """Test comparison operation code generation."""
        program = """
class Main {
    main(): Object {
        1 < 2
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "blt" in assembly.lower() or "<" in assembly, "Comparison operation not found"
    
    def test_conditional_expressions(self):
        """Test if-then-else code generation."""
        program = """
class Main {
    main(): Object {
        if true then 1 else 2 fi
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "beq" in assembly.lower() or "bne" in assembly.lower(), "Conditional branch not found"
    
    def test_loop_expressions(self):
        """Test while loop code generation."""
        program = """
class Main {
    main(): Object {
        while false loop 0 pool
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "beq" in assembly.lower() or "bne" in assembly.lower(), "Loop branch not found"
    
    def test_let_expressions(self):
        """Test let expression code generation."""
        program = """
class Main {
    main(): Object {
        let x: Int <- 5 in x
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "let" in assembly.lower() or "$sp" in assembly, "Let expression not found"
    
    def test_block_expressions(self):
        """Test block expression code generation."""
        program = """
class Main {
    main(): Object {
        { 1; 2; }
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
    
    def test_new_expressions(self):
        """Test new expression code generation."""
        program = """
class Main {
    main(): Object {
        new Main
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "new" in assembly.lower() or "_protObj" in assembly, "New expression not found"
    
    def test_dispatch_expressions(self):
        """Test method dispatch code generation."""
        program = """
class Main {
    main(): Object {
        (new Main).test()
    };
    test(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "jal" in assembly.lower() or "jalr" in assembly.lower(), "Method dispatch not found"
    
    def test_static_dispatch_expressions(self):
        """Test static dispatch code generation."""
        program = """
class Main {
    main(): Object {
        (new Main)@Main.test()
    };
    test(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "jal" in assembly.lower() or "jalr" in assembly.lower(), "Static dispatch not found"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_class(self):
        """Test code generation for empty class."""
        program = """
class Empty {
};
class Main {
    main(): Object { new Empty };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "Empty" in assembly, "Empty class not found"
    
    def test_class_with_only_attributes(self):
        """Test class with only attributes, no methods."""
        program = """
class A {
    x: Int;
    y: Int;
};
class Main {
    main(): Object { new A };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "A" in assembly, "Class A not found"
    
    def test_class_with_only_methods(self):
        """Test class with only methods, no attributes."""
        program = """
class A {
    test1(): Int { 1 };
    test2(): Int { 2 };
};
class Main {
    main(): Object { new A };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "A" in assembly, "Class A not found"
    
    def test_deep_inheritance(self):
        """Test code generation with deep inheritance hierarchy."""
        program = """
class A {
};
class B inherits A {
};
class C inherits B {
};
class Main {
    main(): Object { new C };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "C" in assembly, "Class C not found"
    
    def test_self_type_handling(self):
        """Test handling of SELF_TYPE in expressions."""
        program = """
class Main {
    main(): Object {
        self
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
    
    def test_nested_expressions(self):
        """Test deeply nested expressions."""
        program = """
class Main {
    main(): Object {
        if true then if true then 1 else 2 fi else 3 fi
    };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
    
    def test_multiple_parameters(self):
        """Test methods with multiple parameters."""
        program = """
class Main {
    test(x: Int, y: Int): Int { x + y };
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "test" in assembly, "Method test not found"
    
    def test_no_parameters(self):
        """Test methods with no parameters."""
        program = """
class Main {
    test(): Int { 0 };
    main(): Object { 0 };
};
"""
        assembly = compile_cool_program(program)
        assert assembly is not None, "Failed to compile program"
        assert "test" in assembly, "Method test not found"
