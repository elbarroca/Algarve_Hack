import React from 'react';

interface ProjectCardProps {
  title: string;
  description: string;
  tags: string[];
  imageUrl?: string;
  link?: string;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  title,
  description,
  tags,
  imageUrl,
  link = '#',
}) => {
  return (
    <a
      href={link}
      className="group block bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl overflow-hidden hover:border-slate-600 transform hover:scale-105 transition-all duration-500 cursor-pointer hover:shadow-2xl hover:shadow-blue-500/20"
    >
      {/* Image Section */}
      {imageUrl && (
        <div className="relative h-48 bg-gradient-to-br from-blue-900 to-purple-900 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 group-hover:opacity-0 transition-opacity duration-500" />
          <div className="absolute inset-0 flex items-center justify-center text-6xl opacity-20">
            💻
          </div>
        </div>
      )}

      {/* Content Section */}
      <div className="p-6 space-y-4">
        <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors duration-300">
          {title}
        </h3>
        
        <p className="text-slate-400 leading-relaxed line-clamp-3">
          {description}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 pt-2">
          {tags.map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1 text-xs font-medium bg-blue-500/10 text-blue-300 border border-blue-500/30 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Arrow Icon */}
        <div className="flex items-center text-blue-400 font-medium pt-2 group-hover:translate-x-2 transition-transform duration-300">
          Ver Projeto
          <svg
            className="w-4 h-4 ml-2"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </a>
  );
};

