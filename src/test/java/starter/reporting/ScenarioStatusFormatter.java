package starter.reporting;

import io.cucumber.plugin.ConcurrentEventListener;
import io.cucumber.plugin.event.EventPublisher;
import io.cucumber.plugin.event.Location;
import io.cucumber.plugin.event.Status;
import io.cucumber.plugin.event.TestCase;
import io.cucumber.plugin.event.TestCaseFinished;

public class ScenarioStatusFormatter implements ConcurrentEventListener {

	@Override
	public void setEventPublisher(EventPublisher publisher) {
		publisher.registerHandlerFor(TestCaseFinished.class, this::handleTestCaseFinished);
	}

	private void handleTestCaseFinished(TestCaseFinished event) {
		TestCase testCase = event.getTestCase();
		String status = formatStatus(event.getResult().getStatus());
		String location = formatLocation(testCase);

		System.out.println(status + ": " + testCase.getName() + " # " + location);
	}

	private String formatStatus(Status status) {
		if (status == Status.PASSED) {
			return "SCENARIO PASSED";
		}
		if (status == Status.SKIPPED || status == Status.PENDING) {
			return "SCENARIO SKIPPED";
		}
		return "SCENARIO FAILED";
	}

	private String formatLocation(TestCase testCase) {
		Location location = testCase.getLocation();
		String uri = testCase.getUri() == null ? "unknown" : testCase.getUri().toString();
		if (location == null) {
			return uri;
		}
		return uri + ":" + location.getLine();
	}
}