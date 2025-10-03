/**
 * Project details form component with accessibility features
 */

import { useCalculatorStore } from '../stores/calculatorStore'

export default function ProjectForm() {
  const { project, setProject } = useCalculatorStore()

  return (
    <section className="card" aria-labelledby="project-details-heading">
      <h2 id="project-details-heading" className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6 text-gray-800">
        Project Details
      </h2>

      <div className="space-y-4 sm:space-y-6">
        <div>
          <label htmlFor="project-name" className="label">
            Project Name <span className="text-red-500" aria-label="required">*</span>
          </label>
          <input
            id="project-name"
            type="text"
            className="input-field"
            value={project.project_name}
            onChange={(e) => setProject({ project_name: e.target.value })}
            placeholder="My VMS Project"
            required
            aria-required="true"
            aria-invalid={!project.project_name}
            aria-describedby={!project.project_name ? 'project-name-error' : undefined}
          />
          {!project.project_name && (
            <span id="project-name-error" className="sr-only" role="alert">
              Project name is required
            </span>
          )}
        </div>

        <div>
          <label htmlFor="created-by" className="label">
            Created By <span className="text-red-500" aria-label="required">*</span>
          </label>
          <input
            id="created-by"
            type="text"
            className="input-field"
            value={project.created_by}
            onChange={(e) => setProject({ created_by: e.target.value })}
            placeholder="John Doe"
            required
            aria-required="true"
            aria-invalid={!project.created_by}
            aria-describedby={!project.created_by ? 'created-by-error' : undefined}
          />
          {!project.created_by && (
            <span id="created-by-error" className="sr-only" role="alert">
              Creator name is required
            </span>
          )}
        </div>

        <div>
          <label htmlFor="creator-email" className="label">
            Email <span className="text-red-500" aria-label="required">*</span>
          </label>
          <input
            id="creator-email"
            type="email"
            className="input-field"
            value={project.creator_email}
            onChange={(e) => setProject({ creator_email: e.target.value })}
            placeholder="john@example.com"
            required
            aria-required="true"
            aria-invalid={!project.creator_email}
            aria-describedby={!project.creator_email ? 'creator-email-error' : undefined}
            autoComplete="email"
          />
          {!project.creator_email && (
            <span id="creator-email-error" className="sr-only" role="alert">
              Email is required
            </span>
          )}
        </div>

        <div>
          <label htmlFor="receiver-email" className="label">
            Receiver Email <span className="text-gray-500 text-xs">(Optional)</span>
          </label>
          <input
            id="receiver-email"
            type="email"
            className="input-field"
            value={project.receiver_email || ''}
            onChange={(e) => setProject({ receiver_email: e.target.value })}
            placeholder="client@example.com"
            aria-describedby="receiver-email-help"
            autoComplete="email"
          />
          <span id="receiver-email-help" className="sr-only">
            Optional email address to receive the calculation report
          </span>
        </div>

        <div>
          <label htmlFor="company-name" className="label">
            Company Name <span className="text-gray-500 text-xs">(Optional)</span>
          </label>
          <input
            id="company-name"
            type="text"
            className="input-field"
            value={project.company_name || ''}
            onChange={(e) => setProject({ company_name: e.target.value })}
            placeholder="Acme Security Systems"
            autoComplete="organization"
          />
        </div>

        <div>
          <label htmlFor="project-description" className="label">
            Project Description <span className="text-gray-500 text-xs">(Optional)</span>
          </label>
          <textarea
            id="project-description"
            className="input-field resize-y"
            rows={3}
            value={project.description || ''}
            onChange={(e) => setProject({ description: e.target.value })}
            placeholder="Brief description of the project..."
            aria-describedby="description-help"
            maxLength={500}
          />
          <span id="description-help" className="text-xs text-gray-500 mt-1 block">
            {project.description?.length || 0}/500 characters
          </span>
        </div>
      </div>
    </section>
  )
}

