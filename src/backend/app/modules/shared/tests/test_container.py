"""Tests for dependency injection container."""


from ...auth.domain.interfaces import AuthenticationService
from ...math_solving.domain.interfaces import AIService, MathSolverRepository
from ..container import Container


class TestContainer:
    """Test cases for dependency injection container."""

    def setup_method(self):
        """Set up test fixtures."""
        self.container = Container()

    def test_auth_service_singleton(self):
        """Test that auth service is a singleton."""
        service1 = self.container.auth_service()
        service2 = self.container.auth_service()

        assert service1 is service2
        assert isinstance(service1, AuthenticationService)

    def test_ai_service_singleton(self):
        """Test that AI service is a singleton."""
        service1 = self.container.ai_service()
        service2 = self.container.ai_service()

        assert service1 is service2
        assert isinstance(service1, AIService)

    def test_math_solver_repository_singleton(self):
        """Test that math solver repository is a singleton."""
        repo1 = self.container.math_solver_repository()
        repo2 = self.container.math_solver_repository()

        assert repo1 is repo2
        assert isinstance(repo1, MathSolverRepository)

    def test_use_case_dependencies(self):
        """Test that use cases get proper dependencies."""
        use_case = self.container.solve_math_problem_use_case()

        # Verify use case has the correct dependencies
        assert use_case.ai_service is self.container.ai_service()
        assert use_case.repository is self.container.math_solver_repository()

    def test_container_isolation(self):
        """Test that different container instances are isolated."""
        container1 = Container()
        container2 = Container()

        service1 = container1.auth_service()
        service2 = container2.auth_service()

        # Different containers should have different instances
        assert service1 is not service2
